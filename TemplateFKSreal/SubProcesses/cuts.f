c************************************************************************
c     This function is called from sample to see if it needs to 
c     bother calculating the weight from all the different conficurations
c     You can either just return true, or have it call passcuts
c************************************************************************
      implicit none
c
c     Arguments
c
      double precision p
c
c     External
c
      logical passcuts
      external passcuts
c-----
c  Begin Code
c-----
      pass_point = .true.
c      pass_point = passcuts(p)
      end
C $B$ PASSCUTS $B$ !this is a tag for MadWeight
      LOGICAL FUNCTION PASSCUTS(P,rwgt)
C $E$ PASSCUTS $E$ !this is a tag for MadWeight
C**************************************************************************
C     INPUT:
C            P(0:3,1)           MOMENTUM OF INCOMING PARTON
C            P(0:3,2)           MOMENTUM OF INCOMING PARTON
C            P(0:3,3)           MOMENTUM OF d
C            P(0:3,4)           MOMENTUM OF b
C            P(0:3,5)           MOMENTUM OF bbar
C            P(0:3,6)           MOMENTUM OF e+
C            P(0:3,7)           MOMENTUM OF ve
C            COMMON/JETCUTS/   CUTS ON JETS
C     OUTPUT:
C            TRUE IF EVENTS PASSES ALL CUTS LISTED
C**************************************************************************
C
C *WARNING**WARNING**WARNING**WARNING**WARNING**WARNING**WARNING**WARNING*
C
C In MadFKS, the momenta given in input to this function are in the
C reduced parton c.m. frame. If need be, boost them to the lab frame.
C The rapidity of this boost is
C
C       YBST_TIL_TOLAB
C
C given in the common block /PARTON_CMS_STUFF/
C
C This is the rapidity that enters in the arguments of the sinh() and
C cosh() of the boost, in such a way that
C       ylab = ycm - ybst_til_tolab
C where ylab is the rapidity in the lab frame and ycm the rapidity
C in the center-of-momentum frame.
C
C *WARNING**WARNING**WARNING**WARNING**WARNING**WARNING**WARNING**WARNING*
c
      IMPLICIT NONE
c
c     Constants
c
      include 'genps.inc'
      include "nexternal.inc"
C
C     ARGUMENTS
C
      REAL*8 P(0:3,nexternal),rwgt

C
C     LOCAL
C
      LOGICAL FIRSTTIME,FIRSTTIME2,pass_bw, notgood,good
      LOGICAL nogo(nexternal)
      integer i,j,njets,hardj1,hardj2,skip
      REAL*8 XVAR,ptmax1,ptmax2,htj,cpar,logYcut
      real*8 ptemp(0:3)
C
C     EXTERNAL
C
      REAL*8 R2,DOT,ET,RAP,DJ,SumDot,pt,rewgt
      logical cut_bw
      external cut_bw,rewgt
C
C     GLOBAL
C
      include 'run.inc'
      include 'cuts.inc'

      double precision ybst_til_tolab,ybst_til_tocm,sqrtshat,shat
      common/parton_cms_stuff/ybst_til_tolab,ybst_til_tocm,
     #                        sqrtshat,shat

      double precision ptjet(nexternal)
      double precision temp

      double precision etmin(nincoming+1:nexternal),etamax(nincoming+1:nexternal)
      double precision emin(nincoming+1:nexternal)
      double precision                    r2min(nincoming+1:nexternal,nincoming+1:nexternal)
      double precision s_min(nexternal,nexternal)
      double precision etmax(nincoming+1:nexternal),etamin(nincoming+1:nexternal)
      double precision emax(nincoming+1:nexternal)
      double precision r2max(nincoming+1:nexternal,nincoming+1:nexternal)
      double precision s_max(nexternal,nexternal)
      common/to_cuts/  etmin, emin, etamax, r2min, s_min,
     $     etmax, emax, etamin, r2max, s_max

      double precision ptjmin4(4),ptjmax4(4),htjmin4(2:4),htjmax4(2:4)
      logical jetor
      common/to_jet_cuts/ ptjmin4,ptjmax4,htjmin4,htjmax4,jetor

c
c     Special cuts
c

      integer        lbw(0:nexternal)  !Use of B.W.
      common /to_BW/ lbw
C
C     SPECIAL CUTS
C
C $B$ TO_SPECISA $B$ !this is a tag for MadWeight
      LOGICAL  IS_A_J(NEXTERNAL),IS_A_L(NEXTERNAL)
      LOGICAL  IS_A_B(NEXTERNAL),IS_A_A(NEXTERNAL)
      LOGICAL  IS_A_NU(NEXTERNAL),IS_HEAVY(NEXTERNAL)
      COMMON /TO_SPECISA/IS_A_J,IS_A_A,IS_A_L,IS_A_B,IS_A_NU,IS_HEAVY
C $E$ TO_SPECISA $E$ !this is a tag for MadWeight
      include 'coupl.inc'
C
C
c
      DATA FIRSTTIME,FIRSTTIME2/.TRUE.,.TRUE./

c jet cluster algorithm
      integer NN,NJET,NSUB,JET(nexternal)
      integer NNQCD
      double precision pplab(0:3, nexternal)
      double precision pQCD(0:3,nexternal),PJET(0:3,nexternal)
      double precision rfj,sycut,palg,fastjetdmerge
      double precision d01,d12,d23,d34
      external fastjetdmerge
      double precision ptmin(5)
      integer njetbak
      double precision thispt
      double precision ymaxjet
      double precision getrapidity
      integer igoodjet(nexternal)

      integer mm


      double precision chybst,shybst,chybstmo
      double precision xd(1:3)
      data (xd(i),i=1,3)/0,0,1/
      double precision totpt

C-----
C  BEGIN CODE
C-----



      PASSCUTS=.TRUE.             !EVENT IS OK UNLESS OTHERWISE CHANGED
      IF (FIRSTTIME) THEN
         FIRSTTIME=.FALSE.
c
         write(*,'(a10,10i8)') 'Particle',(i,i=nincoming+1,nexternal)
         write(*,'(a10,10f8.1)') 'Et >',(etmin(i),i=nincoming+1,nexternal)
         write(*,'(a10,10f8.1)') 'E >',(emin(i),i=nincoming+1,nexternal)
         write(*,'(a10,10f8.1)') 'Eta <',(etamax(i),i=nincoming+1,nexternal)
         do j=nincoming+1,nexternal-1
            write(*,'(a,i2,a,10f8.1)') 'd R #',j,'  >',(-0.0,i=nincoming+1,j),
     &           (r2min(i,j),i=j+1,nexternal)
            do i=j+1,nexternal
               r2min(i,j)=r2min(i,j)*dabs(r2min(i,j))    !Since r2 returns distance squared
               r2max(i,j)=r2max(i,j)*dabs(r2max(i,j))
            enddo
         enddo
         do j=1,nexternal-1
            write(*,'(a,i2,a,10f8.1)') 's min #',j,'>',
     &           (s_min(i,j),i=nincoming+1,nexternal)
         enddo

      ENDIF
c
c     Make sure have reasonable 4-momenta
c
      if (p(0,1) .le. 0d0) then
         passcuts=.false.
         return
      endif

c     Also make sure there's no INF or NAN
      do i=1,nexternal
         do j=0,3
            if(p(j,i).gt.1d32.or.p(j,i).ne.p(j,i))then
               passcuts=.false.
               return
            endif
         enddo
      enddo

      rwgt=1d0

c Put all (light) QCD partons in momentum array for jet clustering.
c From the run_card.dat, maxjetflavor defines if b quark should
c be considered here (via the logical variable 'is_a_jet').

      chybst=cosh(ybst_til_tolab)
      shybst=sinh(ybst_til_tolab)
      chybstmo=chybst-1.d0
      do i=3,nexternal
        call boostwdir2(chybst,shybst,chybstmo,xd,
     #                  p(0,i),pplab(0,i))
      enddo

      NN=0
      NNQCD=0
      totpt=0d0
      !prepare boosted momenta to be clustered by jet algo, 
      ! if totpt is large enough
      do j=nincoming+1,nexternal
         if (is_a_j(j)) then
            NN=NN+1
            if (pplab(0,j) .gt.1d-8) then
             NNQCD=NNQCD+1
             totpt = totpt + dsqrt(pplab(1,j)**2 + pplab(2,j)**2)
             do i=0,3
               pQCD(i,NNQCD)=pplab(i,j)
             enddo
            endif
         endif
      enddo

c Cut some peculiar momentum configurations, i.e. two partons very soft
c This is needed to get rid of numerical instabilities in the Real emission
c matrix elements when the Born has a massless final-state parton, but
c no possible divergence related to it (e.g. t-channel single top)
      mm=0
      do j=1,nn
        if(abs(pQCD(0,j)/p(0,1)).lt.1.d-8) mm=mm+1
      enddo
      if(mm.gt.1)then
         passcuts=.false.
         return
      endif

c     uncomment for bypassing jet algo and cuts.
c$$$      goto 123


c Define jet clustering parameters
      palg=1.d0               ! jet algorithm: 1.0=kt, 0.0=C/A, -1.0 = anti-kt
      rfj=0.4d0                 ! the radius parameter
      sycut=60d0

c uncomment the following lines to apply a cut on the sum of the light
c   jet tranverse energies       
ccc      if (totpt .lt. sycut) then
ccc          passcuts =  .false.
ccc          return
ccc      endif


c******************************************************************************
c     call FASTJET to get all the jets
c
c     INPUT:
c     input momenta:               pQCD(0:3,nexternal), energy is 0th component
c     number of input momenta:     NN
c     radius parameter:            rfj
c     minumum jet pt:              sycut
c     jet algorithm:               palg, 1.0=kt, 0.0=C/A, -1.0 = anti-kt
c
c     OUTPUT:
c     jet momenta:                             pjet(0:3,nexternal), E is 0th cmpnt
c     the number of jets (with pt > SYCUT):    njet
c     the jet for a given particle 'i':        jet(i),   note that this is
c     the particle in pQCD, which doesn't necessarily correspond to the particle
c     label in the process
c
ccc----FOR FJ v < 3.0
c      call fastjetppgenkt(pQCD,NN,rfj,sycut,palg,pjet,njet,jet)
ccc----


ccc----FOR FJ v > 3.0
      call fastjetppgenkt(pQCD,NNQCD,rfj,sycut,palg,pjet,njet)


      if (NJET .ne. NN .and. NJET .ne. NN-1) then
         passcuts=.false.
         return
      endif


 123  continue

      RETURN
      END




      subroutine unweight_function(p_born,unwgtfun)
c Dummy function. Should always retrun 1.
      implicit none
      include 'nexternal.inc'
      double precision unwgtfun,p_born(0:3,nexternal-1)
      unwgtfun=1d0
      return
      end

