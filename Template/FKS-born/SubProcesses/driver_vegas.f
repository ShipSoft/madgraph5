      Program DRIVER
c**************************************************************************
c     This is the driver for the whole calulation
c**************************************************************************
      implicit none
C
C     CONSTANTS
C
      double precision zero
      parameter       (ZERO = 0d0)
      include 'genps.inc'
      include 'nexternal.inc'
      INTEGER    ITMAX,   NCALL
      common/citmax/itmax,ncall
C
C     LOCAL
C
      integer i,j,l,l1,l2,ndim
      double precision dsig,tot,mean,sigma
      integer npoints
      double precision x,y,jac,s1,s2,xmin
      external dsig
      character*130 buf
c
c     Global
c
      integer                                      nsteps
      character*40          result_file,where_file
      common /sample_status/result_file,where_file,nsteps
      integer           Minvar(maxdim,lmaxconfigs)
      common /to_invar/ Minvar
      real*8          dsigtot(10)
      common/to_dsig/ dsigtot
      integer ngroup
      common/to_group/ngroup
      data ngroup/0/
cc
      include 'run.inc'
      include 'coupl.inc'
      
      integer           iconfig
      common/to_configs/iconfig


      double precision twgt, maxwgt,swgt(maxevents)
      integer                             lun, nw
      common/to_unwgt/twgt, maxwgt, swgt, lun, nw

c Vegas stuff
      integer ipole
      common/tosigint/ndim,ipole

      real*8 sigint,res,err,chi2a
      external sigint

      integer irestart
      character * 70 idstring
      logical savegrid

      logical            flat_grid
      common/to_readgrid/flat_grid                !Tells if grid read from file

      external initplot

      logical usexinteg,mint
      common/cusexinteg/usexinteg,mint

c For tests
      real*8 fksmaxwgt,xisave,ysave
      common/cfksmaxwgt/fksmaxwgt,xisave,ysave

      integer itotalpoints
      common/ctotalpoints/itotalpoints

c For tests of virtuals
      double precision vobmax,vobmin
      common/cvirt0test/vobmax,vobmin
      double precision vNsumw,vAsumw,vSsumw,vNsumf,vAsumf,vSsumf
      common/cvirt1test/vNsumw,vAsumw,vSsumw,vNsumf,vAsumf,vSsumf
      integer nvtozero
      logical doVirtTest
      common/cvirt2test/nvtozero,doVirtTest
      integer ivirtpoints,ivirtpointsExcept
      double precision  virtmax,virtmin,virtsum
      common/cvirt3test/virtmax,virtmin,virtsum,ivirtpoints,
     &     ivirtpointsExcept
      double precision total_wgt_sum,total_wgt_sum_max,
     &                 total_wgt_sum_min
      common/csum_of_wgts/total_wgt_sum,total_wgt_sum_max,
     &                 total_wgt_sum_min

      integer n_mp, n_disc
c     $B$ new_def $E$  this is a tag for MadWeigth, Don't edit this line

c      double precision xsec,xerr
c      integer ncols,ncolflow(maxamps),ncolalt(maxamps),ic
c      common/to_colstats/ncols,ncolflow,ncolalt,ic
C-----
C  BEGIN CODE
C-----  
c
c     Read process number
c
      open (unit=lun+1,file='../dname.mg',status='unknown',err=11)
      read (lun+1,'(a130)',err=11,end=11) buf
      l1=index(buf,'P')
      l2=index(buf,'_')
      if(l1.ne.0.and.l2.ne.0.and.l1.lt.l2-1)
     $     read(buf(l1+1:l2-1),*,err=11) ngroup
 11   print *,'Process in group number ',ngroup

      lun = 27
      twgt = -2d0            !determine wgt after first iteration
      open(unit=lun,status='scratch')
      nsteps=2
      call setrun                !Sets up run parameters
      call setpara('param_card.dat')   !Sets up couplings and masses
      call setcuts               !Sets up cuts and particle masses
      call printout              !Prints out a summary of paramaters
      call run_printout          !Prints out a summary of the run settings
c     
c     Get user input
c
      write(*,*) "getting user params"
      call get_user_params(ncall,itmax,iconfig,irestart,idstring,savegrid)
      if(irestart.eq.1)then
        flat_grid=.true.
      else
        flat_grid=.false.
      endif
c$$$      call setfksfactor(iconfig)
      ndim = 3*(nexternal-2)-4
      if (abs(lpp(1)) .ge. 1) ndim=ndim+1
      if (abs(lpp(2)) .ge. 1) ndim=ndim+1

c Don't proceed if muF1#muF2 (we need to work out the relevant formulae
c at the NLO)
      if( ( fixed_fac_scale .and.
     #       (muF1_over_ref*muF1_ref_fixed) .ne.
     #       (muF2_over_ref*muF2_ref_fixed) ) .or.
     #    ( (.not.fixed_fac_scale) .and.
     #      muF1_over_ref.ne.muF2_over_ref ) )then
        write(*,*)'NLO computations require muF1=muF2'
        stop
      endif

      write(*,*) "about to integrate ", ndim,ncall,itmax,iconfig

      if(doVirtTest)then
        vobmax=-1.d8
        vobmin=1.d8
        vNsumw=0.d0
        vAsumw=0.d0
        vSsumw=0.d0
        vNsumf=0.d0
        vAsumf=0.d0
        vSsumf=0.d0
        nvtozero=0
        virtmax=-1d99
        virtmin=1d99
        virtsum=0d0
      endif
      itotalpoints=0
      ivirtpoints=0
      ivirtpointsExcept=0
      total_wgt_sum=0d0
      total_wgt_sum_max=0d0
      total_wgt_sum_min=0d0

      if(savegrid)then
        call integrate(initplot,sigint,idstring,itmax,irestart,ndim,ncall,
     #                 res,err,chi2a,savegrid)
        usexinteg=.false.
      else
        call initplot
        call xinteg(sigint,ndim,itmax,ncall,res,err)
        usexinteg=.true.
      endif

      write (*,*) ''
      write (*,*) '----------------------------------------------------'
      write(*,*)'Final result:',res,'+/-',err
      write(*,*)'Maximum weight found:',fksmaxwgt
      write(*,*)'Found for:',xisave,ysave
      write (*,*) '----------------------------------------------------'
      write (*,*) ''

      if(doVirtTest)then
        write(*,*)'  '
        write(*,*)'Statistics for virtuals'
        write(*,*)'max[V/(as/(2*pi)B)]:',vobmax
        write(*,*)'min[V/(as/(2*pi)B)]:',vobmin
        if(vNsumw.ne.0.d0)then
          vAsumw=vAsumw/vNsumw
          vSsumw=vSsumw/vNsumw
          write(*,*)'Weighted:'
          write(*,*)'  average=',vAsumw
          if(vSsumw.lt.(vAsumw**2*0.9999d0))then
            write(*,*)'Error in sigma',vSsumw,vAsumw
          else
            write(*,*)'  std dev=',sqrt(abs(vSsumw-vAsumw**2))
          endif
        else
          write(*,*)'Sum of weights [virt_w] is zero'
        endif
c
        if(vNsumf.ne.0.d0)then
          vAsumf=vAsumf/vNsumf
          vSsumf=vSsumf/vNsumf
          write(*,*)'Flat:'
          write(*,*)'  average=',vAsumf
          if(vSsumf.lt.(vAsumf**2*0.9999d0))then
            write(*,*)'Error in sigma',vSsumf,vAsumf
          else
            write(*,*)'  std dev=',sqrt(abs(vSsumf-vAsumf**2))
          endif
        else
          write(*,*)'Sum of weights [virt_f] is zero'
        endif
c
        if(nvtozero.ne.0)then
          write(*,*)
     &          '# of points (passing cuts) with Born=0 and virt=0:',
     &          nvtozero
        endif
        write (*,*) 'virtual weights directly from LesHouches.f:'
        if (ivirtpoints.ne.0) then
           write (*,*) 'max(virtual/Born/ao2pi)= ',virtmax
           write (*,*) 'min(virtual/Born/ao2pi)= ',virtmin
           write (*,*) 'avg(virtual/Born/ao2pi)= ',
     &          virtsum/dble(ivirtpoints)
        endif
      endif

      write (*,*) ''
      write (*,*) '----------------------------------------------------'
      if (irestart.eq.1 .or. irestart.eq.3) then
         write (*,*) 'Total points tried:                   ',
     &        ncall*itmax
         write (*,*) 'Total points passing generation cuts: ',
     &        itotalpoints
         write (*,*) 'Efficiency of events passing cuts:    ',
     &        dble(itotalpoints)/dble(ncall*itmax)
      else
         write (*,*)
     &       'Run has been restarted, next line is only for current run'
         write (*,*) 'Total points passing cuts: ',itotalpoints
      endif
      write (*,*) '----------------------------------------------------'
      write (*,*) ''
      write (*,*) ''
      write (*,*) '----------------------------------------------------'
      write (*,*) 'number of except PS points:',ivirtpointsExcept,
     &     'out of',ivirtpoints,'points'
      write (*,*) '   treatment of exceptional PS points:'
      write (*,*) '      maximum approximation:',
     &     total_wgt_sum + dsqrt(total_wgt_sum_max)
      write (*,*) '      minimum approximation:',
     &     total_wgt_sum - dsqrt(total_wgt_sum_min)
      write (*,*) '      taking the max/min average:',total_wgt_sum
      write (*,*) '----------------------------------------------------'
      write (*,*) ''

c Uncomment for getting CutTools statistics
c$$$      call ctsstatistics(n_mp,n_disc)
c$$$      write(*,*) 'n_mp  =',n_mp,'    n_disc=',n_disc


      if(savegrid)call initplot
      call mclear
      open(unit=99,file='MADatNLO.top',status='unknown')
      call topout
      close(99)

      end


      function sigint(xx,peso)
c From dsample_fks
      implicit none
      include 'nexternal.inc'
      real*8 sigint,peso,xx(58)
      integer ione
      parameter (ione=1)
      integer ndim
      common/tosigint/ndim
      integer           iconfig
      common/to_configs/iconfig
      integer i
      double precision wgt,dsig,ran2,rnd
      external ran2
      double precision x(99),p(0:3,nexternal)
      include 'fks_info.inc'
      INTEGER NFKSPROCESS
      COMMON/C_NFKSPROCESS/NFKSPROCESS
      character*4 abrv
      common /to_abrv/ abrv
      logical nbodyonly
      common/cnbodyonly/nbodyonly
      integer fks_j_from_i(nexternal,0:nexternal)
     &     ,particle_type(nexternal),pdg_type(nexternal)
      common /c_fks_inc/fks_j_from_i,particle_type,pdg_type
      integer i_fks,j_fks
      common/fks_indices/i_fks,j_fks
      logical sum,firsttime
      parameter (sum=.false.)
      data firsttime /.true./
      integer nFKSprocessBorn
      save nFKSprocessBorn
      double precision vol

c
      do i=1,99
        if(i.le.ndim)then
         x(i)=xx(i)
        else
          x(i)=0.d0
        endif
      enddo
      sigint=0d0

c Find the nFKSprocess for which we compute the Born-like contributions
      if (firsttime) then
         firsttime=.false.
         nFKSprocess=fks_configs
         call fks_inc_chooser()
         do while (particle_type(i_fks).ne.8)
            write (*,*) i_fks,particle_type(i_fks)
            nFKSprocess=nFKSprocess-1
            call fks_inc_chooser()
            if (nFKSprocess.eq.0) then
               write (*,*) 'ERROR in sigint'
               stop
            endif
         enddo
         nFKSprocessBorn=nFKSprocess
      endif
         
c
c Compute the Born-like contributions with nbodyonly=.true.
c THIS CAN BE OPTIMIZED
c
      nFKSprocess=nFKSprocessBorn
      abrv='bsv '
      nbodyonly=.true.
      call fks_inc_chooser()
      call leshouche_inc_chooser()
      call setcuts
      call setfksfactor(iconfig)
      wgt=1d0
      call generate_momenta(ndim,iconfig,wgt,x,p)

      sigint = sigint+dsig(p,wgt,peso)

      nbodyonly=.false.

c
c Compute the subtracted real-emission corrections either as an explicit
c sum or a Monte Carlo sum.
c      
      if (sum) then
c THIS CAN BE OPTIMIZED
         abrv='nbsv'
         do nFKSprocess=1,fks_configs
            call fks_inc_chooser()
            call leshouche_inc_chooser()
            call setcuts
            call setfksfactor(iconfig)
            wgt=1d0
            call generate_momenta(ndim,iconfig,wgt,x,p)
            sigint = sigint+dsig(p,wgt,peso)
         enddo
      else ! Monte Carlo over nFKSprocess
c$$$         rnd=xx(ndim+1)
         call get_MC_integer(fks_configs,nFKSprocess,vol)
c$$$         rnd=ran2()
c$$$         nFKSprocess=0
c$$$         do while (nFKSprocess.lt.rnd*fks_configs)
c$$$            nFKSprocess=nFKSprocess+1
c$$$         enddo
c THIS CAN BE OPTIMIZED
         abrv='nbsv'
         call fks_inc_chooser()
         call leshouche_inc_chooser()
         call setcuts
         call setfksfactor(iconfig)
         wgt=1d0
         call generate_momenta(ndim,iconfig,wgt,x,p)
         sigint = sigint+
     &        dsig(p,wgt,peso*fks_configs/vol)*fks_configs/vol
      endif
      call fill_MC_integer(nFKSprocess,abs(sigint)*peso)

      return
      end

c
      subroutine get_user_params(ncall,itmax,iconfig,
     #                           irestart,idstring,savegrid)
c**********************************************************************
c     Routine to get user specified parameters for run
c**********************************************************************
      implicit none
c
c     Constants
c
      include 'genps.inc'
      include 'nexternal.inc'
c
c     Arguments
c
      integer ncall,itmax,iconfig, jconfig
c
c     Local
c
      integer i, j
      double precision dconfig
c
c     Global
c
      integer           isum_hel
      logical                   multi_channel
      common/to_matrix/isum_hel, multi_channel
      double precision    accur
      common /to_accuracy/accur
      integer           use_cut
      common /to_weight/use_cut

      integer        lbw(0:nexternal)  !Use of B.W.
      common /to_BW/ lbw

      character*5 abrvinput
      character*4 abrv
      common /to_abrv/ abrv

      logical nbodyonly
      common/cnbodyonly/nbodyonly

      integer nvtozero
      logical doVirtTest
      common/cvirt2test/nvtozero,doVirtTest
c
c To convert diagram number to configuration
c
      integer iforest(2,-max_branch:-1,lmaxconfigs)
      integer sprop(-max_branch:-1,lmaxconfigs)
      integer tprid(-max_branch:-1,lmaxconfigs)
      integer mapconfig(0:lmaxconfigs)
      include 'born_conf.inc'
c
c Vegas stuff
c
      integer irestart,itmp
      character * 70 idstring
      logical savegrid

      character * 80 runstr
      common/runstr/runstr
      logical usexinteg,mint
      common/cusexinteg/usexinteg,mint
      logical unwgt
      double precision evtsgn
      common /c_unwgt/evtsgn,unwgt

c-----
c  Begin Code
c-----
      doVirtTest=.true.
      mint=.false.
      unwgt=.false.
      write(*,'(a)') 'Enter number of events and iterations: '
      read(*,*) ncall,itmax
      write(*,*) 'Number of events and iterations ',ncall,itmax
      write(*,'(a)') 'Enter desired fractional accuracy: '
      read(*,*) accur
      write(*,*) 'Desired fractional accuracy: ',accur

      write(*,'(a)') 'Enter 0 for fixed, 2 for adjustable grid: '
      read(*,*) use_cut
      if (use_cut .lt. 0 .or. use_cut .gt. 2) then
         write(*,*) 'Bad choice, using 2',use_cut
         use_cut = 2
      endif

      write(*,10) 'Suppress amplitude (0 no, 1 yes)? '
      read(*,*) i
      if (i .eq. 1) then
         multi_channel = .true.
         write(*,*) 'Using suppressed amplitude.'
      else
         multi_channel = .false.
         write(*,*) 'Using full amplitude.'
      endif

      write(*,10) 'Exact helicity sum (0 yes, n = number/event)? '
      read(*,*) i
      if (i .eq. 0) then
         isum_hel = 0
         write(*,*) 'Explicitly summing over helicities'
      else
         isum_hel= i
         write(*,*) 'Summing over',i,' helicities/event'
      endif

      write(*,10) 'Enter Configuration Number: '
      read(*,*) dconfig
      iconfig = int(dconfig)
      do i=1,mapconfig(0)
         if (iconfig.eq.mapconfig(i)) then
            iconfig=i
            exit
         endif
      enddo
      write(*,12) 'Running Configuration Number: ',iconfig
c
c Enter parameters that control Vegas grids
c
      write(*,*)'enter id string for this run'
      read(*,*) idstring
      runstr=idstring
      write(*,*)'enter 1 if you want restart files'
      read (*,*) itmp
      if(itmp.eq.1) then
         savegrid = .true.
      else
         savegrid = .false.
      endif
      write(*,*)'enter 0 to exclude, 1 for new run, 2 to restart'
      read(5,*)irestart

      abrvinput='     '
      write (*,*) "'all ', 'born', 'real', 'virt', 'novi' or 'grid'?"
      write (*,*) "Enter 'born0' or 'virt0' to perform"
      write (*,*) " a pure n-body integration (no S functions)"
      read(5,*) abrvinput
      if(abrvinput(5:5).eq.'0')then
        nbodyonly=.true.
      else
        nbodyonly=.false.
      endif
      abrv=abrvinput(1:4)
c Options are way too many: make sure we understand all of them
      if ( abrv.ne.'all '.and.abrv.ne.'born'.and.abrv.ne.'real'.and.
     &     abrv.ne.'virt'.and.abrv.ne.'novi'.and.abrv.ne.'grid'.and.
     &     abrv.ne.'viSC'.and.abrv.ne.'viLC'.and.abrv.ne.'novA'.and.
     &     abrv.ne.'novB'.and.abrv.ne.'viSA'.and.abrv.ne.'viSB') then
        write(*,*)'Error in input: abrv is:',abrv
        stop
      endif
      if(nbodyonly.and.abrv.ne.'born'.and.abrv(1:2).ne.'vi'
     &     .and. abrv.ne.'grid')then
        write(*,*)'Error in driver: inconsistent input',abrvinput
        stop
      endif

      write (*,*) "doing the ",abrv," of this channel"
      if(nbodyonly)then
        write (*,*) "integration Born/virtual with Sfunction=1"
      else
        write (*,*) "Normal integration (Sfunction != 1)"
      endif

      doVirtTest=doVirtTest.and.abrv(1:2).eq.'vi'
c
c
c     Here I want to set up with B.W. we map and which we don't
c
      dconfig = dconfig-iconfig
      if (dconfig .eq. 0) then
         write(*,*) 'Not subdividing B.W.'
         lbw(0)=0
      else
         lbw(0)=1
         jconfig=dconfig*1000.1
         write(*,*) 'Using dconfig=',jconfig
         call DeCode(jconfig,lbw(1),3,nexternal)
         write(*,*) 'BW Setting ', (lbw(j),j=1,nexternal-2)
c         do i=nexternal-3,0,-1
c            if (jconfig .ge. 2**i) then
c               lbw(i+1)=1
c               jconfig=jconfig-2**i
c            else
c               lbw(i+1)=0
c            endif 
c            write(*,*) i+1, lbw(i+1)
c         enddo
      endif
 10   format( a)
 12   format( a,i4)
      end
c


      subroutine get_MC_integer(fks_configs,iint,vol)
      implicit none
      integer iint,i
      double precision ran2,rnd,vol
      external ran2
      logical firsttime
      data firsttime/.true./
      integer nintervals,maxintervals,fks_configs
      parameter (maxintervals=1000)
      integer ncall(0:maxintervals)
      double precision grid(0:maxintervals),acc(0:maxintervals)
      common/integration_integer/grid,acc,ncall,nintervals
      if (firsttime) then
         firsttime=.false.
         nintervals=fks_configs
         do i=0,nintervals
            grid(i)=dble(i)/nintervals
            acc(i)=0d0
            ncall(i)=0
         enddo
      endif
      rnd=ran2()
      iint=0
      do while (rnd .gt. grid(iint))
         iint=iint+1
      enddo
      if (iint.eq.0 .or. iint.gt.nintervals) then
         write (*,*) 'ERROR in get_MC_integer',iint,nintervals,grid
         stop
      endif
      vol=(grid(iint)-grid(iint-1))*nintervals
      ncall(iint)=ncall(iint)+1
      return
      end

      subroutine fill_MC_integer(iint,f_abs)
      implicit none
      integer iint
      double precision f_abs
      integer nintervals,maxintervals
      parameter (maxintervals=1000)
      integer ncall(0:maxintervals)
      double precision grid(0:maxintervals),acc(0:maxintervals)
      common/integration_integer/grid,acc,ncall,nintervals
      acc(iint)=acc(iint)+f_abs
      return
      end

      subroutine regrid_MC_integer
      implicit none
      integer i,ib
      double precision tiny
      parameter ( tiny=1d-3 )
      character*101 buff
      integer nintervals,maxintervals
      parameter (maxintervals=1000)
      integer ncall(0:maxintervals)
      double precision grid(0:maxintervals),acc(0:maxintervals)
      common/integration_integer/grid,acc,ncall,nintervals
c      write (*,*) ncall
c      write (*,*) acc
c      write (*,*) grid
      do i=1,101
         buff(i:i)=' '
      enddo
      do i=0,nintervals
         ib=1+int(grid(i)*100)
         write (buff(ib:ib),'(i1)') mod(i,10)
      enddo
      write (*,*) 'nFKSprocess ',buff

c Compute the accumulated cross section
      do i=1,nintervals
         if(ncall(i).ne.0) then
            acc(i)=acc(i-1)+acc(i)
         else
            acc(i)=acc(i-1)
         endif
      enddo
c Define the new grids
      do i=0,nintervals
         grid(i)=acc(i)/acc(nintervals)
      enddo

c Check that we have a reasonable result and update the accumulated
c results if need be
      do i=1,nintervals
         if (grid(i).le.(grid(i-1)+tiny)) then
c$$$            write (*,*) 'Accumulated results for nFKSprocess '/
c$$$     &           /' need adaptation #1:'
c$$$            write (*,*) grid(i),grid(i-1),' become'
            grid(i)=grid(i-1)+tiny
c$$$            write (*,*) grid(i),grid(i-1)
         endif
      enddo
c it could happen that the change above yielded grid() values greater
c than 1; should be fixed once more.
      grid(nintervals)=1d0
      do i=1,nintervals
         if (grid(nintervals-i).ge.(grid(nintervals-i+1)-tiny)) then
c$$$            write (*,*) 'Accumulated results for nFKSprocess '/
c$$$     &           /'need adaptation #2:'
c$$$            write (*,*) grid(nintervals-i),grid(nintervals-i+1)
c$$$     &           ,' become'
            grid(nintervals-i)=1d0-dble(i)*tiny
c$$$            write (*,*) grid(nintervals-i),grid(nintervals-i+1)
         else
            exit
         endif
      enddo

c Reset the accumalated results because we start new iteration.
      do i=0,nintervals
         acc(i)=0d0
         ncall(i)=0
      enddo
      return
      end
