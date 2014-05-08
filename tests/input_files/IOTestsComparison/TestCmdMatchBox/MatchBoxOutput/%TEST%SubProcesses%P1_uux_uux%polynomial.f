C     THE SUBROUTINE TO CREATE THE COEFFICIENTS FROM LAST LOOP WF AND 
C     MULTIPLY BY THE BORN

      SUBROUTINE P1_CREATE_LOOP_COEFS(LOOP_WF,RANK,LCUT_SIZE,LOOP_COEFS
     $ ,SYMFACT,COLOR_ID,HELCONFIG)
      IMPLICIT NONE
C     
C     CONSTANTS 
C     
      INTEGER NBORNAMPS
      PARAMETER (NBORNAMPS=2)
      COMPLEX*16 IMAG1
      PARAMETER (IMAG1=(0D0,1D0))
      INTEGER MAXLWFSIZE
      PARAMETER (MAXLWFSIZE=4)
      INTEGER LOOPMAXCOEFS
      PARAMETER (LOOPMAXCOEFS=15)
      INTEGER    NCOLORROWS
      PARAMETER (NCOLORROWS=82)
      INTEGER    NLOOPGROUPS
      PARAMETER (NLOOPGROUPS=13)
      INTEGER    NCOMB
      PARAMETER (NCOMB=16)
C     
C     ARGUMENTS 
C     
      COMPLEX*16 LOOP_WF(MAXLWFSIZE,0:LOOPMAXCOEFS-1,MAXLWFSIZE)
      INTEGER RANK, COLOR_ID, SYMFACT, LCUT_SIZE, HELCONFIG
      COMPLEX*16 LOOP_COEFS(LOOPMAXCOEFS)
C     
C     LOCAL VARIABLES 
C     
      COMPLEX*16 CFTOT
      COMPLEX*16 CONST
      INTEGER I,H
C     
C     GLOBAL VARIABLES
C     
      INTEGER CF_D(NCOLORROWS,NBORNAMPS)
      INTEGER CF_N(NCOLORROWS,NBORNAMPS)
      COMMON/P1_CF/CF_D,CF_N

      LOGICAL CHECKPHASE
      LOGICAL HELDOUBLECHECKED
      COMMON/P1_INIT/CHECKPHASE, HELDOUBLECHECKED

      INTEGER HELOFFSET
      INTEGER GOODHEL(NCOMB)
      LOGICAL GOODAMP(NLOOPGROUPS)
      COMMON/P1_FILTERS/GOODAMP,GOODHEL,HELOFFSET

      INTEGER HELPICKED
      COMMON/P1_HELCHOICE/HELPICKED

      COMPLEX*16 AMP(NBORNAMPS)
      COMMON/AMPS/AMP

      CONST=(0.0D0,0.0D0)

      DO I=1,NBORNAMPS
        CFTOT=DCMPLX(CF_N(COLOR_ID,I)/DBLE(ABS(CF_D(COLOR_ID,I)))
     $   ,0.0D0)
        IF(CF_D(COLOR_ID,I).LT.0) CFTOT=CFTOT*IMAG1
        CONST=CONST+CFTOT*DCONJG(AMP(I))
      ENDDO
      CONST=CONST/SYMFACT
      IF (.NOT.CHECKPHASE.AND.HELDOUBLECHECKED.AND.HELPICKED.EQ.
     $ -1) THEN
        CONST=CONST*GOODHEL(HELCONFIG)
      ENDIF
      CALL P1_MERGE_WL(LOOP_WF,RANK,LCUT_SIZE,CONST,LOOP_COEFS)

      END

      SUBROUTINE MP_P1_CREATE_LOOP_COEFS(LOOP_WF,RANK,LCUT_SIZE
     $ ,LOOP_COEFS,SYMFACT,COLOR_ID,HELCONFIG)
C     
C     CONSTANTS 
C     
      INTEGER NBORNAMPS
      PARAMETER (NBORNAMPS=2)
      COMPLEX*32 IMAG1
      PARAMETER (IMAG1=(0E0_16,1E0_16))
      INTEGER MAXLWFSIZE
      PARAMETER (MAXLWFSIZE=4)
      INTEGER LOOPMAXCOEFS
      PARAMETER (LOOPMAXCOEFS=15)
      INTEGER    NCOLORROWS
      PARAMETER (NCOLORROWS=82)
      INTEGER    NLOOPGROUPS
      PARAMETER (NLOOPGROUPS=13)
      INTEGER    NCOMB
      PARAMETER (NCOMB=16)
C     
C     ARGUMENTS 
C     
      COMPLEX*32 LOOP_WF(MAXLWFSIZE,0:LOOPMAXCOEFS-1,MAXLWFSIZE)
      INTEGER RANK, COLOR_ID, SYMFACT, LCUT_SIZE, HELCONFIG
      COMPLEX*32 LOOP_COEFS(LOOPMAXCOEFS)
C     
C     LOCAL VARIABLES 
C     
      COMPLEX*32 CFTOT
      COMPLEX*32 CONST
      INTEGER I,H
C     
C     GLOBAL VARIABLES
C     
      INTEGER CF_D(NCOLORROWS,NBORNAMPS)
      INTEGER CF_N(NCOLORROWS,NBORNAMPS)
      COMMON/P1_CF/CF_D,CF_N

      LOGICAL CHECKPHASE
      LOGICAL HELDOUBLECHECKED
      COMMON/P1_INIT/CHECKPHASE, HELDOUBLECHECKED

      INTEGER HELOFFSET
      INTEGER GOODHEL(NCOMB)
      LOGICAL GOODAMP(NLOOPGROUPS)
      COMMON/P1_FILTERS/GOODAMP,GOODHEL,HELOFFSET

      INTEGER HELPICKED
      COMMON/HELCHOICE/HELPICKED

      COMPLEX*32 AMP(NBORNAMPS)
      COMMON/MP_AMPS/AMP

      CONST=(0.0E0_16,0.0E0_16)

      DO I=1,NBORNAMPS
        CFTOT=CMPLX(CF_N(COLOR_ID,I)/REAL(ABS(CF_D(COLOR_ID,I))
     $   ,KIND=16),0.0E0_16,KIND=16)
        IF(CF_D(COLOR_ID,I).LT.0) CFTOT=CFTOT*IMAG1
        CONST=CONST+CFTOT*CONJG(AMP(I))
      ENDDO
      CONST=CONST/SYMFACT
      IF (.NOT.CHECKPHASE.AND.HELDOUBLECHECKED.AND.HELPICKED.EQ.
     $ -1) THEN
        CONST=CONST*GOODHEL(HELCONFIG)
      ENDIF
      CALL MP_P1_MERGE_WL(LOOP_WF,RANK,LCUT_SIZE,CONST,LOOP_COEFS)

      END


      SUBROUTINE P1_EVAL_POLY(C,R,Q,OUT)
      INCLUDE 'coef_specs.inc'
      COMPLEX*16 C(0:LOOP_MAXCOEFS-1)
      INTEGER R
      COMPLEX*16 Q(0:3)
      COMPLEX*16 OUT

      OUT=C(0)
      IF (R.GE.1) THEN
        OUT=OUT+C(1)*Q(0)+C(2)*Q(1)+C(3)*Q(2)+C(4)*Q(3)
      ENDIF
      IF (R.GE.2) THEN
        OUT=OUT+C(5)*Q(0)*Q(0)+C(6)*Q(0)*Q(1)+C(7)*Q(0)*Q(2)+C(8)*Q(0)
     $   *Q(3)+C(9)*Q(1)*Q(1)+C(10)*Q(1)*Q(2)+C(11)*Q(1)*Q(3)
     $   +C(12)*Q(2)*Q(2)+C(13)*Q(2)*Q(3)+C(14)*Q(3)*Q(3)
      ENDIF
      END

      SUBROUTINE MP_P1_EVAL_POLY(C,R,Q,OUT)
      INCLUDE 'coef_specs.inc'
      COMPLEX*32 C(0:LOOP_MAXCOEFS-1)
      INTEGER R
      COMPLEX*32 Q(0:3)
      COMPLEX*32 OUT

      OUT=C(0)
      IF (R.GE.1) THEN
        OUT=OUT+C(1)*Q(0)+C(2)*Q(1)+C(3)*Q(2)+C(4)*Q(3)
      ENDIF
      IF (R.GE.2) THEN
        OUT=OUT+C(5)*Q(0)*Q(0)+C(6)*Q(0)*Q(1)+C(7)*Q(0)*Q(2)+C(8)*Q(0)
     $   *Q(3)+C(9)*Q(1)*Q(1)+C(10)*Q(1)*Q(2)+C(11)*Q(1)*Q(3)
     $   +C(12)*Q(2)*Q(2)+C(13)*Q(2)*Q(3)+C(14)*Q(3)*Q(3)
      ENDIF
      END

      SUBROUTINE P1_ADD_COEFS(A,RA,B,RB)
      INCLUDE 'coef_specs.inc'
      INTEGER I
      COMPLEX*16 A(0:LOOP_MAXCOEFS-1),B(0:LOOP_MAXCOEFS-1)
      INTEGER RA,RB

      INTEGER NCOEF_R(0:2)
      DATA NCOEF_R/1,5,15/

      DO I=0,NCOEF_R(RB)-1
        A(I)=A(I)+B(I)
      ENDDO
      END

      SUBROUTINE MP_P1_ADD_COEFS(A,RA,B,RB)
      INCLUDE 'coef_specs.inc'
      INTEGER I
      COMPLEX*32 A(0:LOOP_MAXCOEFS-1),B(0:LOOP_MAXCOEFS-1)
      INTEGER RA,RB

      INTEGER NCOEF_R(0:2)
      DATA NCOEF_R/1,5,15/

      DO I=0,NCOEF_R(RB)-1
        A(I)=A(I)+B(I)
      ENDDO
      END

      SUBROUTINE P1_MERGE_WL(WL,R,LCUT_SIZE,CONST,OUT)
      INCLUDE 'coef_specs.inc'
      INTEGER I,J
      COMPLEX*16 WL(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      INTEGER R,LCUT_SIZE
      COMPLEX*16 CONST
      COMPLEX*16 OUT(0:LOOP_MAXCOEFS-1)

      INTEGER NCOEF_R(0:2)
      DATA NCOEF_R/1,5,15/

      DO I=1,LCUT_SIZE
        DO J=0,NCOEF_R(R)-1
          OUT(J)=OUT(J)+WL(I,J,I)*CONST
        ENDDO
      ENDDO
      END

      SUBROUTINE MP_P1_MERGE_WL(WL,R,LCUT_SIZE,CONST,OUT)
      INCLUDE 'coef_specs.inc'
      INTEGER I,J
      COMPLEX*32 WL(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      INTEGER R,LCUT_SIZE
      COMPLEX*32 CONST
      COMPLEX*32 OUT(0:LOOP_MAXCOEFS-1)

      INTEGER NCOEF_R(0:2)
      DATA NCOEF_R/1,5,15/

      DO I=1,LCUT_SIZE
        DO J=0,NCOEF_R(R)-1
          OUT(J)=OUT(J)+WL(I,J,I)*CONST
        ENDDO
      ENDDO
      END

      SUBROUTINE P1_UPDATE_WL_0_1(A,LCUT_SIZE,B,IN_SIZE,OUT_SIZE,OUT)
      INCLUDE 'coef_specs.inc'
      INTEGER I,J,K
      COMPLEX*16 A(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*16 B(MAXLWFSIZE,0:VERTEXMAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*16 OUT(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      INTEGER LCUT_SIZE,IN_SIZE,OUT_SIZE

      DO I=1,LCUT_SIZE
        DO J=1,OUT_SIZE
          DO K=0,4
            OUT(J,K,I)=(0.0D0,0.0D0)
          ENDDO
          DO K=1,IN_SIZE
            OUT(J,0,I)=OUT(J,0,I)+A(K,0,I)*B(J,0,K)
            OUT(J,1,I)=OUT(J,1,I)+A(K,0,I)*B(J,1,K)
            OUT(J,2,I)=OUT(J,2,I)+A(K,0,I)*B(J,2,K)
            OUT(J,3,I)=OUT(J,3,I)+A(K,0,I)*B(J,3,K)
            OUT(J,4,I)=OUT(J,4,I)+A(K,0,I)*B(J,4,K)
          ENDDO
        ENDDO
      ENDDO
      END

      SUBROUTINE MP_P1_UPDATE_WL_0_1(A,LCUT_SIZE,B,IN_SIZE,OUT_SIZE
     $ ,OUT)
      INCLUDE 'coef_specs.inc'
      INTEGER I,J,K
      COMPLEX*32 A(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*32 B(MAXLWFSIZE,0:VERTEXMAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*32 OUT(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      INTEGER LCUT_SIZE,IN_SIZE,OUT_SIZE

      DO I=1,LCUT_SIZE
        DO J=1,OUT_SIZE
          DO K=0,4
            OUT(J,K,I)=CMPLX(0.0E0_16,0.0E0_16,KIND=16)
          ENDDO
          DO K=1,IN_SIZE
            OUT(J,0,I)=OUT(J,0,I)+A(K,0,I)*B(J,0,K)
            OUT(J,1,I)=OUT(J,1,I)+A(K,0,I)*B(J,1,K)
            OUT(J,2,I)=OUT(J,2,I)+A(K,0,I)*B(J,2,K)
            OUT(J,3,I)=OUT(J,3,I)+A(K,0,I)*B(J,3,K)
            OUT(J,4,I)=OUT(J,4,I)+A(K,0,I)*B(J,4,K)
          ENDDO
        ENDDO
      ENDDO
      END

      SUBROUTINE P1_UPDATE_WL_2_0(A,LCUT_SIZE,B,IN_SIZE,OUT_SIZE,OUT)
      INCLUDE 'coef_specs.inc'
      INTEGER I,J,K
      COMPLEX*16 A(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*16 B(MAXLWFSIZE,0:VERTEXMAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*16 OUT(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      INTEGER LCUT_SIZE,IN_SIZE,OUT_SIZE

      DO I=1,LCUT_SIZE
        DO J=1,OUT_SIZE
          DO K=0,14
            OUT(J,K,I)=(0.0D0,0.0D0)
          ENDDO
          DO K=1,IN_SIZE
            OUT(J,0,I)=OUT(J,0,I)+A(K,0,I)*B(J,0,K)
            OUT(J,1,I)=OUT(J,1,I)+A(K,1,I)*B(J,0,K)
            OUT(J,2,I)=OUT(J,2,I)+A(K,2,I)*B(J,0,K)
            OUT(J,3,I)=OUT(J,3,I)+A(K,3,I)*B(J,0,K)
            OUT(J,4,I)=OUT(J,4,I)+A(K,4,I)*B(J,0,K)
            OUT(J,5,I)=OUT(J,5,I)+A(K,5,I)*B(J,0,K)
            OUT(J,6,I)=OUT(J,6,I)+A(K,6,I)*B(J,0,K)
            OUT(J,7,I)=OUT(J,7,I)+A(K,7,I)*B(J,0,K)
            OUT(J,8,I)=OUT(J,8,I)+A(K,8,I)*B(J,0,K)
            OUT(J,9,I)=OUT(J,9,I)+A(K,9,I)*B(J,0,K)
            OUT(J,10,I)=OUT(J,10,I)+A(K,10,I)*B(J,0,K)
            OUT(J,11,I)=OUT(J,11,I)+A(K,11,I)*B(J,0,K)
            OUT(J,12,I)=OUT(J,12,I)+A(K,12,I)*B(J,0,K)
            OUT(J,13,I)=OUT(J,13,I)+A(K,13,I)*B(J,0,K)
            OUT(J,14,I)=OUT(J,14,I)+A(K,14,I)*B(J,0,K)
          ENDDO
        ENDDO
      ENDDO
      END

      SUBROUTINE MP_P1_UPDATE_WL_2_0(A,LCUT_SIZE,B,IN_SIZE,OUT_SIZE
     $ ,OUT)
      INCLUDE 'coef_specs.inc'
      INTEGER I,J,K
      COMPLEX*32 A(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*32 B(MAXLWFSIZE,0:VERTEXMAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*32 OUT(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      INTEGER LCUT_SIZE,IN_SIZE,OUT_SIZE

      DO I=1,LCUT_SIZE
        DO J=1,OUT_SIZE
          DO K=0,14
            OUT(J,K,I)=CMPLX(0.0E0_16,0.0E0_16,KIND=16)
          ENDDO
          DO K=1,IN_SIZE
            OUT(J,0,I)=OUT(J,0,I)+A(K,0,I)*B(J,0,K)
            OUT(J,1,I)=OUT(J,1,I)+A(K,1,I)*B(J,0,K)
            OUT(J,2,I)=OUT(J,2,I)+A(K,2,I)*B(J,0,K)
            OUT(J,3,I)=OUT(J,3,I)+A(K,3,I)*B(J,0,K)
            OUT(J,4,I)=OUT(J,4,I)+A(K,4,I)*B(J,0,K)
            OUT(J,5,I)=OUT(J,5,I)+A(K,5,I)*B(J,0,K)
            OUT(J,6,I)=OUT(J,6,I)+A(K,6,I)*B(J,0,K)
            OUT(J,7,I)=OUT(J,7,I)+A(K,7,I)*B(J,0,K)
            OUT(J,8,I)=OUT(J,8,I)+A(K,8,I)*B(J,0,K)
            OUT(J,9,I)=OUT(J,9,I)+A(K,9,I)*B(J,0,K)
            OUT(J,10,I)=OUT(J,10,I)+A(K,10,I)*B(J,0,K)
            OUT(J,11,I)=OUT(J,11,I)+A(K,11,I)*B(J,0,K)
            OUT(J,12,I)=OUT(J,12,I)+A(K,12,I)*B(J,0,K)
            OUT(J,13,I)=OUT(J,13,I)+A(K,13,I)*B(J,0,K)
            OUT(J,14,I)=OUT(J,14,I)+A(K,14,I)*B(J,0,K)
          ENDDO
        ENDDO
      ENDDO
      END

      SUBROUTINE P1_UPDATE_WL_1_0(A,LCUT_SIZE,B,IN_SIZE,OUT_SIZE,OUT)
      INCLUDE 'coef_specs.inc'
      INTEGER I,J,K
      COMPLEX*16 A(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*16 B(MAXLWFSIZE,0:VERTEXMAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*16 OUT(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      INTEGER LCUT_SIZE,IN_SIZE,OUT_SIZE

      DO I=1,LCUT_SIZE
        DO J=1,OUT_SIZE
          DO K=0,4
            OUT(J,K,I)=(0.0D0,0.0D0)
          ENDDO
          DO K=1,IN_SIZE
            OUT(J,0,I)=OUT(J,0,I)+A(K,0,I)*B(J,0,K)
            OUT(J,1,I)=OUT(J,1,I)+A(K,1,I)*B(J,0,K)
            OUT(J,2,I)=OUT(J,2,I)+A(K,2,I)*B(J,0,K)
            OUT(J,3,I)=OUT(J,3,I)+A(K,3,I)*B(J,0,K)
            OUT(J,4,I)=OUT(J,4,I)+A(K,4,I)*B(J,0,K)
          ENDDO
        ENDDO
      ENDDO
      END

      SUBROUTINE MP_P1_UPDATE_WL_1_0(A,LCUT_SIZE,B,IN_SIZE,OUT_SIZE
     $ ,OUT)
      INCLUDE 'coef_specs.inc'
      INTEGER I,J,K
      COMPLEX*32 A(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*32 B(MAXLWFSIZE,0:VERTEXMAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*32 OUT(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      INTEGER LCUT_SIZE,IN_SIZE,OUT_SIZE

      DO I=1,LCUT_SIZE
        DO J=1,OUT_SIZE
          DO K=0,4
            OUT(J,K,I)=CMPLX(0.0E0_16,0.0E0_16,KIND=16)
          ENDDO
          DO K=1,IN_SIZE
            OUT(J,0,I)=OUT(J,0,I)+A(K,0,I)*B(J,0,K)
            OUT(J,1,I)=OUT(J,1,I)+A(K,1,I)*B(J,0,K)
            OUT(J,2,I)=OUT(J,2,I)+A(K,2,I)*B(J,0,K)
            OUT(J,3,I)=OUT(J,3,I)+A(K,3,I)*B(J,0,K)
            OUT(J,4,I)=OUT(J,4,I)+A(K,4,I)*B(J,0,K)
          ENDDO
        ENDDO
      ENDDO
      END

      SUBROUTINE P1_UPDATE_WL_0_0(A,LCUT_SIZE,B,IN_SIZE,OUT_SIZE,OUT)
      INCLUDE 'coef_specs.inc'
      INTEGER I,J,K
      COMPLEX*16 A(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*16 B(MAXLWFSIZE,0:VERTEXMAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*16 OUT(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      INTEGER LCUT_SIZE,IN_SIZE,OUT_SIZE

      DO I=1,LCUT_SIZE
        DO J=1,OUT_SIZE
          DO K=0,0
            OUT(J,K,I)=(0.0D0,0.0D0)
          ENDDO
          DO K=1,IN_SIZE
            OUT(J,0,I)=OUT(J,0,I)+A(K,0,I)*B(J,0,K)
          ENDDO
        ENDDO
      ENDDO
      END

      SUBROUTINE MP_P1_UPDATE_WL_0_0(A,LCUT_SIZE,B,IN_SIZE,OUT_SIZE
     $ ,OUT)
      INCLUDE 'coef_specs.inc'
      INTEGER I,J,K
      COMPLEX*32 A(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*32 B(MAXLWFSIZE,0:VERTEXMAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*32 OUT(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      INTEGER LCUT_SIZE,IN_SIZE,OUT_SIZE

      DO I=1,LCUT_SIZE
        DO J=1,OUT_SIZE
          DO K=0,0
            OUT(J,K,I)=CMPLX(0.0E0_16,0.0E0_16,KIND=16)
          ENDDO
          DO K=1,IN_SIZE
            OUT(J,0,I)=OUT(J,0,I)+A(K,0,I)*B(J,0,K)
          ENDDO
        ENDDO
      ENDDO
      END

      SUBROUTINE P1_UPDATE_WL_1_1(A,LCUT_SIZE,B,IN_SIZE,OUT_SIZE,OUT)
      INCLUDE 'coef_specs.inc'
      INTEGER I,J,K
      COMPLEX*16 A(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*16 B(MAXLWFSIZE,0:VERTEXMAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*16 OUT(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      INTEGER LCUT_SIZE,IN_SIZE,OUT_SIZE

      DO I=1,LCUT_SIZE
        DO J=1,OUT_SIZE
          DO K=0,14
            OUT(J,K,I)=(0.0D0,0.0D0)
          ENDDO
          DO K=1,IN_SIZE
            OUT(J,0,I)=OUT(J,0,I)+A(K,0,I)*B(J,0,K)
            OUT(J,1,I)=OUT(J,1,I)+A(K,0,I)*B(J,1,K)+A(K,1,I)*B(J,0,K)
            OUT(J,2,I)=OUT(J,2,I)+A(K,0,I)*B(J,2,K)+A(K,2,I)*B(J,0,K)
            OUT(J,3,I)=OUT(J,3,I)+A(K,0,I)*B(J,3,K)+A(K,3,I)*B(J,0,K)
            OUT(J,4,I)=OUT(J,4,I)+A(K,0,I)*B(J,4,K)+A(K,4,I)*B(J,0,K)
            OUT(J,5,I)=OUT(J,5,I)+A(K,1,I)*B(J,1,K)
            OUT(J,6,I)=OUT(J,6,I)+A(K,1,I)*B(J,2,K)+A(K,2,I)*B(J,1,K)
            OUT(J,7,I)=OUT(J,7,I)+A(K,1,I)*B(J,3,K)+A(K,3,I)*B(J,1,K)
            OUT(J,8,I)=OUT(J,8,I)+A(K,1,I)*B(J,4,K)+A(K,4,I)*B(J,1,K)
            OUT(J,9,I)=OUT(J,9,I)+A(K,2,I)*B(J,2,K)
            OUT(J,10,I)=OUT(J,10,I)+A(K,2,I)*B(J,3,K)+A(K,3,I)*B(J,2,K)
            OUT(J,11,I)=OUT(J,11,I)+A(K,2,I)*B(J,4,K)+A(K,4,I)*B(J,2,K)
            OUT(J,12,I)=OUT(J,12,I)+A(K,3,I)*B(J,3,K)
            OUT(J,13,I)=OUT(J,13,I)+A(K,3,I)*B(J,4,K)+A(K,4,I)*B(J,3,K)
            OUT(J,14,I)=OUT(J,14,I)+A(K,4,I)*B(J,4,K)
          ENDDO
        ENDDO
      ENDDO
      END

      SUBROUTINE MP_P1_UPDATE_WL_1_1(A,LCUT_SIZE,B,IN_SIZE,OUT_SIZE
     $ ,OUT)
      INCLUDE 'coef_specs.inc'
      INTEGER I,J,K
      COMPLEX*32 A(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*32 B(MAXLWFSIZE,0:VERTEXMAXCOEFS-1,MAXLWFSIZE)
      COMPLEX*32 OUT(MAXLWFSIZE,0:LOOP_MAXCOEFS-1,MAXLWFSIZE)
      INTEGER LCUT_SIZE,IN_SIZE,OUT_SIZE

      DO I=1,LCUT_SIZE
        DO J=1,OUT_SIZE
          DO K=0,14
            OUT(J,K,I)=CMPLX(0.0E0_16,0.0E0_16,KIND=16)
          ENDDO
          DO K=1,IN_SIZE
            OUT(J,0,I)=OUT(J,0,I)+A(K,0,I)*B(J,0,K)
            OUT(J,1,I)=OUT(J,1,I)+A(K,0,I)*B(J,1,K)+A(K,1,I)*B(J,0,K)
            OUT(J,2,I)=OUT(J,2,I)+A(K,0,I)*B(J,2,K)+A(K,2,I)*B(J,0,K)
            OUT(J,3,I)=OUT(J,3,I)+A(K,0,I)*B(J,3,K)+A(K,3,I)*B(J,0,K)
            OUT(J,4,I)=OUT(J,4,I)+A(K,0,I)*B(J,4,K)+A(K,4,I)*B(J,0,K)
            OUT(J,5,I)=OUT(J,5,I)+A(K,1,I)*B(J,1,K)
            OUT(J,6,I)=OUT(J,6,I)+A(K,1,I)*B(J,2,K)+A(K,2,I)*B(J,1,K)
            OUT(J,7,I)=OUT(J,7,I)+A(K,1,I)*B(J,3,K)+A(K,3,I)*B(J,1,K)
            OUT(J,8,I)=OUT(J,8,I)+A(K,1,I)*B(J,4,K)+A(K,4,I)*B(J,1,K)
            OUT(J,9,I)=OUT(J,9,I)+A(K,2,I)*B(J,2,K)
            OUT(J,10,I)=OUT(J,10,I)+A(K,2,I)*B(J,3,K)+A(K,3,I)*B(J,2,K)
            OUT(J,11,I)=OUT(J,11,I)+A(K,2,I)*B(J,4,K)+A(K,4,I)*B(J,2,K)
            OUT(J,12,I)=OUT(J,12,I)+A(K,3,I)*B(J,3,K)
            OUT(J,13,I)=OUT(J,13,I)+A(K,3,I)*B(J,4,K)+A(K,4,I)*B(J,3,K)
            OUT(J,14,I)=OUT(J,14,I)+A(K,4,I)*B(J,4,K)
          ENDDO
        ENDDO
      ENDDO
      END
