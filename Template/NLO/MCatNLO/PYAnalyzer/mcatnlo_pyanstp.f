C----------------------------------------------------------------------
      SUBROUTINE RCLOS()
C     DUMMY IF HBOOK IS USED
C----------------------------------------------------------------------
      END


C----------------------------------------------------------------------
      SUBROUTINE PYABEG
C     USER'S ROUTINE FOR INITIALIZATION
C----------------------------------------------------------------------
      implicit none
      REAL*8 pi
      PARAMETER (PI=3.14159265358979312D0)
      integer j,kk,jj

      call inihist
      kk=0
      call mbook(kk+ 1,'t pt',5d0,0d0,200d0)
      call mbook(kk+ 2,'t log pt',0.05d0,0d0,5d0)
      call mbook(kk+ 3,'t y',0.25d0,-6d0,6d0)
      call mbook(kk+ 4,'t eta',0.25d0,-6d0,6d0)
c
      call mbook(kk+ 5,'j1 pt',5d0,0d0,200d0)
      call mbook(kk+ 6,'j1 log pt',0.05d0,0d0,5d0)
      call mbook(kk+ 7,'j1 y',0.25d0,-6d0,6d0)
      call mbook(kk+ 8,'j1 eta',0.25d0,-6d0,6d0)
c
      call mbook(kk+ 9,'j2 pt',5d0,0d0,200d0)
      call mbook(kk+10,'j2 log pt',0.05d0,0d0,5d0)
      call mbook(kk+11,'j2 y',0.25d0,-6d0,6d0)
      call mbook(kk+12,'j2 eta',0.25d0,-6d0,6d0)
c
      call mbook(kk+13,'bj1 pt',5d0,0d0,200d0)
      call mbook(kk+14,'bj1 log pt',0.05d0,0d0,5d0)
      call mbook(kk+15,'bj1 y',0.25d0,-6d0,6d0)
      call mbook(kk+16,'bj1 eta',0.25d0,-6d0,6d0)
c
      call mbook(kk+17,'bj2 pt',5d0,0d0,200d0)
      call mbook(kk+18,'bj2 log pt',0.05d0,0d0,5d0)
      call mbook(kk+19,'bj2 y',0.25d0,-6d0,6d0)
      call mbook(kk+20,'bj2 eta',0.25d0,-6d0,6d0)
c
      call mbook(kk+21,'syst pt',5d0,0d0,200d0)
      call mbook(kk+22,'syst log pt',0.05d0,0d0,5d0)
      call mbook(kk+23,'syst y',0.25d0,-6d0,6d0)
      call mbook(kk+24,'syst eta',0.25d0,-6d0,6d0)
c
      END


C----------------------------------------------------------------------
      SUBROUTINE PYAEND(IEVT)
C     USER'S ROUTINE FOR TERMINAL CALCULATIONS, HISTOGRAM OUTPUT, ETC
C----------------------------------------------------------------------
      implicit none
      REAL*8 XNORM
      INTEGER I,J,K,ievt
      OPEN(UNIT=99,FILE='PYTST.top',STATUS='UNKNOWN')
C XNORM IS SUCH THAT THE CROSS SECTION PER BIN IS IN PB, SINCE THE HERWIG 
C WEIGHT IS IN NB, AND CORRESPONDS TO THE AVERAGE CROSS SECTION
      XNORM=1.D0/IEVT
      DO I=1,500              
 	CALL MFINAL3(I)             
        CALL MCOPY(I,I+500)
        CALL MOPERA(I+500,'F',I+500,I+500,(XNORM),0.D0)
 	CALL MFINAL3(I+500)
      ENDDO

C
      k=0
      call multitop(500+k+ 1,499,2,3,'t pt',' ','LOG')
      call multitop(500+k+ 2,499,2,3,'t log pt',' ','LOG')
      call multitop(500+k+ 3,499,2,3,'t y',' ','LOG')
      call multitop(500+k+ 4,499,2,3,'t eta',' ','LOG')
c
      call multitop(500+k+ 5,499,2,3,'j1 pt',' ','LOG')
      call multitop(500+k+ 6,499,2,3,'j1 log pt',' ','LOG')
      call multitop(500+k+ 7,499,2,3,'j1 y',' ','LOG')
      call multitop(500+k+ 8,499,2,3,'j1 eta',' ','LOG')
c
      call multitop(500+k+ 9,499,2,3,'j2 pt',' ','LOG')
      call multitop(500+k+10,499,2,3,'j2 log pt',' ','LOG')
      call multitop(500+k+11,499,2,3,'j2 y',' ','LOG')
      call multitop(500+k+12,499,2,3,'j2 eta',' ','LOG')
c
      call multitop(500+k+13,499,2,3,'bj1 pt',' ','LOG')
      call multitop(500+k+14,499,2,3,'bj1 log pt',' ','LOG')
      call multitop(500+k+15,499,2,3,'bj1 y',' ','LOG')
      call multitop(500+k+16,499,2,3,'bj1 eta',' ','LOG')
c
      call multitop(500+k+17,499,2,3,'bj2 pt',' ','LOG')
      call multitop(500+k+18,499,2,3,'bj2 log pt',' ','LOG')
      call multitop(500+k+19,499,2,3,'bj2 y',' ','LOG')
      call multitop(500+k+20,499,2,3,'bj2 eta',' ','LOG')
c
      call multitop(500+k+21,499,2,3,'syst pt',' ','LOG')
      call multitop(500+k+22,499,2,3,'syst log pt',' ','LOG')
      call multitop(500+k+23,499,2,3,'syst y',' ','LOG')
      call multitop(500+k+24,499,2,3,'syst eta',' ','LOG')
c
      CLOSE(99)
      END


C----------------------------------------------------------------------
      SUBROUTINE PYANAL
C     USER'S ROUTINE TO ANALYSE DATA FROM EVENT
C     BASED ON AN ANALYSIS FILE WRITTEN BY E.RE
C----------------------------------------------------------------------
      implicit none
      DOUBLE PRECISION HWVDOT,PSUM(4)
      REAL*8 PI
      PARAMETER (PI=3.14159265358979312D0)
      REAL*8 WWW0
      INTEGER kk,mu,jpart,i,j,ihep,ichsum,nt,nb,nbjets,ist,id,
     &njets,id1,i1,i2,ibmatch,ichini,k,ihadr,count_j,count_bj
      integer maxtrack,maxjet,maxnum
      parameter (maxtrack=2048,maxjet=2048,maxnum=30)
      integer ntracks,jetvec(maxtrack),ib1
      double precision pttop,etatop,ytop,ptj1,etaj1,yj1,ptbj1,etabj1,
     &ybj1,ptbj2,etabj2,ybj2,jet_ktradius,jet_ktptmin,palg,pttemp_spec,
     &pttemp_bjet,pttemp,tmp,getrapidity,getpseudorap,getpt,
     &pjet(4,maxtrack),ptrack(4,maxtrack),p_top(4,maxnum),p_b(4,maxnum),
     &p_bjet(4,maxnum),psyst(4),ptsyst,ysyst,etasyst,ptj2,yj2,etaj2
      logical is_b_jet(maxnum)
      integer btrack(maxnum),ib(maxnum)
c
      integer pychge,n,npad
      double precision p,v
      external pydata
      common/pyjets/n,npad,k(4000,5),p(4000,5),v(4000,5)
      DOUBLE PRECISION EVWEIGHT,p1(4),p2(4),pihep(4),vdot
      COMMON/CEVWEIGHT/EVWEIGHT
      INTEGER IFAIL
      COMMON/CIFAIL/IFAIL

c
      IF (IFAIL.EQ.1) RETURN
C INCOMING PARTONS MAY TRAVEL IN THE SAME DIRECTION: IT'S A POWER-SUPPRESSED
C EFFECT, SO THROW THE EVENT AWAY
      IF(SIGN(1.D0,P(3,3)).EQ.SIGN(1.D0,P(4,3)))THEN
         WRITE(*,*)'WARNING 111 IN PYANAL'
         GOTO 999
      ENDIF
      WWW0=EVWEIGHT
      DO I=1,4
         P1(I)=P(1,I)
         P2(I)=P(2,I)
      ENDDO
      CALL VVSUM(4,P1,P2,PSUM)
      CALL VSCA(4,-1D0,PSUM,PSUM)
      ICHSUM=0
      ICHINI=PYCHGE(K(1,2))+PYCHGE(K(2,2))

C INITIALIZE
      NT=0
      NB=0
      NBJETS=0
      NTRACKS=0
      NJETS=0

      DO IHEP=1,N
        DO J=1,4
          PIHEP(J)=P(IHEP,J)
        ENDDO
        IST=K(IHEP,1)
        ID=K(IHEP,2)
        ID1=IHADR(ID)          ! equal to the PDG of the massive quark in hadron
        IF (IST.LE.10) THEN
          CALL VVSUM(4,PIHEP,PSUM,PSUM)
          ICHSUM=ICHSUM+PYCHGE(ID)
         ENDIF
C TOP
        IF(ABS(ID).EQ.6) THEN
           DO MU=1,4
              P_TOP(MU,1)=P(IHEP,MU)
           ENDDO
        ENDIF
c Define particles that go into jet. 
        IF (IST.LE.10.AND.ABS(ID).GE.100)THEN
           NTRACKS=NTRACKS+1
           if (abs(id1).eq.5) THEN
c FOUND A stable B-FLAVOURED HADRON.
              NB=NB+1
              IB(NB)=IHEP
              DO MU=1,4
                 P_B(MU,NB)=P(IHEP,MU)
              ENDDO
              BTRACK(NB)=NTRACKS
           endif
           DO MU=1,4
              PTRACK(MU,NTRACKS)=P(IHEP,MU)
           ENDDO
           IF(NTRACKS.EQ.MAXTRACK) THEN
              WRITE(*,*)'PYANAL: TOO MANY PARTICLES, INCREASE MAXTRACK'
              STOP
           ENDIF
        ENDIF
      ENDDO
C END OF LOOP OVER IHEP

C CHECK MOMENTUM AND CHARGE CONSERVATION
      IF (VDOT(3,PSUM,PSUM).GT.1.E-4*P(1,4)**2) THEN
         WRITE(*,*)'WARNING 112 IN PYANAL'
         GOTO 999
      ENDIF
      IF (ICHSUM.NE.ICHINI) THEN
         WRITE(*,*)'WARNING 113 IN PYANAL'
         GOTO 999
      ENDIF

      IF (NTRACKS.EQ.0) THEN
         WRITE(*,*) 'NO TRACKS FOUND, DROP ANALYSIS OF THIS EVENT'
         GOTO 999
      ENDIF
         
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
C KT ALGORITHM, FASTJET IMPLEMENTATION
CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
      NJETS=0
      JET_KTRADIUS = 0.7D0          
      JET_KTPTMIN  = 5D0
      PALG=1D0
      CALL fastjetppgenkt(PTRACK,NTRACKS,JET_KTRADIUS,JET_KTPTMIN,PALG,
     $     PJET,NJETS,JETVEC)

c Check that jets are ordered in pt
      do i=1,njets-1
         if (getpt(pjet(1,i)).lt.getpt(pjet(1,i+1)) ) then
            write (*,*) 'ERROR jets not ordered'
            stop
         endif
      enddo
         
C TAG B-FLAVOURED JETS 
      nbjets=0
      do i=1,njets
         is_b_jet(i)=.false.
         do j=1,NB
            if (JETVEC(BTRACK(j)).eq.i) then
c B-jet found
               is_b_jet(i)=.true.
               exit
            endif
         enddo
         if (is_b_jet(i)) then
            nbjets=nbjets+1
            do mu=1,4
               p_bjet(mu,nbjets)=pjet(mu,i)
            enddo
         endif
      enddo

      kk=0
      pttop = getpt(p_top(1,1))
      ytop  = getrapidity(p_top(1,1))
      etatop= getpseudorap(p_top(1,1))
      call mfill(kk+1,(pttop),(www0))
      if(pttop.gt.0d0)
     &call mfill(kk+2,(log10(pttop)),(www0))
      call mfill(kk+3,(ytop),(www0))
      call mfill(kk+4,(etatop),(www0))

      count_j=1
      do i=1,njets
         if(.not.is_b_jet(i))then
            if(count_j.eq.1)then
               ptj1 = getpt(pjet(1,i))
               yj1  = getrapidity(pjet(1,i))
               etaj1= getpseudorap(pjet(1,i))
               call mfill(kk+5,(ptj1),(www0))
               call mfill(kk+6,(log10(ptj1)),(www0))
               call mfill(kk+7,(yj1),(www0))
               call mfill(kk+8,(etaj1),(www0))
               do mu=1,4
                  psyst(mu)=p_top(mu,1)+pjet(mu,i)
               enddo
               ptsyst = getpt(psyst)
               ysyst  = getrapidity(psyst)
               etasyst= getpseudorap(psyst)
               call mfill(kk+21,(ptsyst),(www0))
               if(ptsyst.gt.0d0)
     &         call mfill(kk+22,(log10(ptsyst)),(www0))
               call mfill(kk+23,(ysyst),(www0))
               call mfill(kk+24,(etasyst),(www0))
            elseif(count_j.eq.2)then
               ptj2 = getpt(pjet(1,i))
               yj2  = getrapidity(pjet(1,i))
               etaj2= getpseudorap(pjet(1,i))
               call mfill(kk+9,(ptj2),(www0))
               call mfill(kk+10,(log10(ptj2)),(www0))
               call mfill(kk+11,(yj2),(www0))
               call mfill(kk+12,(etaj2),(www0))
            elseif(count_j.eq.3)then
               exit
            endif
            count_j=count_j+1
         endif
      enddo
      
      count_bj=1
      do i=1,nbjets
            if (count_bj.eq.1) then
               ptbj1 = getpt(p_bjet(1,i))
               ybj1  = getrapidity(p_bjet(1,i))
               etabj1= getpseudorap(p_bjet(1,i))
               call mfill(kk+13,(ptbj1),(www0))
               call mfill(kk+14,(log10(ptbj1)),(www0))
               call mfill(kk+15,(ybj1),(www0))
               call mfill(kk+16,(etabj1),(www0))
            elseif (count_bj.eq.2) then
               ptbj2 = getpt(p_bjet(1,i))
               ybj2  = getrapidity(p_bjet(1,i))
               etabj2= getpseudorap(p_bjet(1,i))
               call mfill(kk+17,(ptbj2),(www0))
               call mfill(kk+18,(log10(ptbj2)),(www0))
               call mfill(kk+19,(ybj2),(www0))
               call mfill(kk+20,(etabj2),(www0))
            elseif(count_bj.eq.3)then
               exit
            endif
            count_bj=count_bj+1
         enddo

 999  RETURN
      END


      function getrapidity(p)
      implicit none
      real*8 getrapidity,en,pl,tiny,xplus,xminus,y,p(4)
      parameter (tiny=1.d-5)
c
      en=p(4)
      pl=p(3)
      xplus=en+pl
      xminus=en-pl
      if(xplus.gt.tiny.and.xminus.gt.tiny)then
        if( (xplus/xminus).gt.tiny )then
          y=0.5d0*log( xplus/xminus )
        else
          y=sign(1.d0,pl)*1.d8
        endif
      else
        y=sign(1.d0,pl)*1.d8
      endif
      getrapidity=y
      return
      end


      function getpseudorap(p)
      implicit none
      real*8 getpseudorap,en,ptx,pty,pl,tiny,pt,eta,th,p(4)
      parameter (tiny=1.d-5)
c
      en=p(4)
      ptx=p(1)
      pty=p(2)
      pl=p(3)
      pt=sqrt(ptx**2+pty**2)
      if(pt.lt.tiny.and.abs(pl).lt.tiny)then
        eta=sign(1.d0,pl)*1.d8
      else
        th=atan2(pt,pl)
        eta=-log(tan(th/2.d0))
      endif
      getpseudorap=eta
      return
      end

      function getpt(p)
      implicit none
      real*8 getpt,p(4)
      getpt=dsqrt(p(1)**2+p(2)**2)
      return
      end

      function getinvm(en,ptx,pty,pl)
      implicit none
      real*8 getinvm,en,ptx,pty,pl,tiny,tmp
      parameter (tiny=1.d-5)
c
      tmp=en**2-ptx**2-pty**2-pl**2
      if(tmp.gt.0.d0)then
        tmp=sqrt(tmp)
      elseif(tmp.gt.-tiny)then
        tmp=0.d0
      else
        write(*,*)'Attempt to compute a negative mass'
        stop
      endif
      getinvm=tmp
      return
      end


      function getdelphi(ptx1,pty1,ptx2,pty2)
      implicit none
      real*8 getdelphi,ptx1,pty1,ptx2,pty2,tiny,pt1,pt2,tmp
      parameter (tiny=1.d-5)
c
      pt1=sqrt(ptx1**2+pty1**2)
      pt2=sqrt(ptx2**2+pty2**2)
      if(pt1.ne.0.d0.and.pt2.ne.0.d0)then
        tmp=ptx1*ptx2+pty1*pty2
        tmp=tmp/(pt1*pt2)
        if(abs(tmp).gt.1.d0+tiny)then
          write(*,*)'Cosine larger than 1'
          stop
        elseif(abs(tmp).ge.1.d0)then
          tmp=sign(1.d0,tmp)
        endif
        tmp=acos(tmp)
      else
        tmp=1.d8
      endif
      getdelphi=tmp
      return
      end


      FUNCTION IHADR(ID)
c Returns the PDG code of the heavier quark in the hadron of PDG code ID
      IMPLICIT NONE
      INTEGER IHADR,ID,ID1
C
      IF(ID.NE.0)THEN
        ID1=ABS(ID)
        IF(ID1.GT.10000)ID1=ID1-1000*INT(ID1/1000)
        IHADR=ID1/(10**INT(LOG10(DFLOAT(ID1))))
      ELSE
        IHADR=0
      ENDIF
      RETURN
      END



C-----------------------------------------------------------------------
      SUBROUTINE VVSUM(N,P,Q,R)
C-----------------------------------------------------------------------
C    VECTOR SUM
C-----------------------------------------------------------------------
      IMPLICIT NONE
      INTEGER N,I
      DOUBLE PRECISION P(N),Q(N),R(N)
      DO 10 I=1,N
   10 R(I)=P(I)+Q(I)
      END



C-----------------------------------------------------------------------
      SUBROUTINE VSCA(N,C,P,Q)
C-----------------------------------------------------------------------
C     VECTOR TIMES SCALAR
C-----------------------------------------------------------------------
      IMPLICIT NONE
      INTEGER N,I
      DOUBLE PRECISION C,P(N),Q(N)
      DO 10 I=1,N
   10 Q(I)=C*P(I)
      END



C-----------------------------------------------------------------------
      FUNCTION VDOT(N,P,Q)
C-----------------------------------------------------------------------
C     VECTOR DOT PRODUCT
C-----------------------------------------------------------------------
      IMPLICIT NONE
      INTEGER N,I
      DOUBLE PRECISION VDOT,PQ,P(N),Q(N)
      PQ=0.
      DO 10 I=1,N
   10 PQ=PQ+P(I)*Q(I)
      VDOT=PQ
      END
