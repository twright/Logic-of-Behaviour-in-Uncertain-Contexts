/* A Bison parser, made by GNU Bison 3.0.5.  */

/* Bison implementation for Yacc-like parsers in C

   Copyright (C) 1984, 1989-1990, 2000-2015, 2018 Free Software Foundation, Inc.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* C LALR(1) parser skeleton written by Richard Stallman, by
   simplifying the original so-called "semantic" parser.  */

/* All symbols defined below should begin with yy or YY, to avoid
   infringing on user name space.  This should be done even for local
   variables, as they might otherwise be expanded by user macros.
   There are some unavoidable exceptions within include files to
   define necessary library symbols; they are noted "INFRINGES ON
   USER NAME SPACE" below.  */

/* Identify Bison output.  */
#define YYBISON 1

/* Bison version.  */
#define YYBISON_VERSION "3.0.5"

/* Skeleton name.  */
#define YYSKELETON_NAME "yacc.c"

/* Pure parsers.  */
#define YYPURE 0

/* Push parsers.  */
#define YYPUSH 0

/* Pull parsers.  */
#define YYPULL 1




/* Copy the first part of user declarations.  */
#line 1 "modelParser.y" /* yacc.c:339  */

	/*---
	Flow*: A Verification Tool for Cyber-Physical Systems.
	Authors: Xin Chen, Sriram Sankaranarayanan, and Erika Abraham.
	Email: Xin Chen <chenxin415@gmail.com> if you have questions or comments.

	The code is released as is under the GNU General Public License (GPL).
	---*/


	#include "modelParser.h"
	#include <string>

	extern int yyerror(const char *);
	extern int yyerror(std::string);
	extern int yylex();
	extern int yyparse();
	bool err;

	int lineNum = 1;

	flowstar::ContinuousReachability continuousProblem;
	flowstar::HybridReachability hybridProblem;
	flowstar::ReachabilitySetting mode_local_setting;

	flowstar::iMatrix dyn_A;
	flowstar::iMatrix dyn_A_row;

	flowstar::iMatrix dyn_B;
	flowstar::iMatrix dyn_B_row;

	flowstar::iMatrix dyn_ti;
	flowstar::iMatrix dyn_ti_row;

	flowstar::iMatrix dyn_tv;
	flowstar::iMatrix dyn_tv_row;

	flowstar::upMatrix dyn_A_t;
	flowstar::upMatrix dyn_A_t_row;

	flowstar::upMatrix dyn_B_t;
	flowstar::upMatrix dyn_B_t_row;

	flowstar::upMatrix dyn_ti_t;
	flowstar::upMatrix dyn_ti_t_row;

	flowstar::upMatrix dyn_tv_t;
	flowstar::upMatrix dyn_tv_t_row;

	VarList varlist;

	std::vector<flowstar::Flowpipe> initialSets;

	void parseError(const char *str, int lnum)
	{
		std::cerr << "Error @line " << lineNum << ":" << std::string(str) << std::endl;
		exit(1);
	}

#line 126 "modelParser.tab.c" /* yacc.c:339  */

# ifndef YY_NULLPTR
#  if defined __cplusplus && 201103L <= __cplusplus
#   define YY_NULLPTR nullptr
#  else
#   define YY_NULLPTR 0
#  endif
# endif

/* Enabling verbose error messages.  */
#ifdef YYERROR_VERBOSE
# undef YYERROR_VERBOSE
# define YYERROR_VERBOSE 1
#else
# define YYERROR_VERBOSE 0
#endif

/* In a future release of Bison, this section will be replaced
   by #include "modelParser.tab.h".  */
#ifndef YY_YY_MODELPARSER_TAB_H_INCLUDED
# define YY_YY_MODELPARSER_TAB_H_INCLUDED
/* Debug traces.  */
#ifndef YYDEBUG
# define YYDEBUG 0
#endif
#if YYDEBUG
extern int yydebug;
#endif

/* Token type.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
  enum yytokentype
  {
    NUM = 258,
    IDENT = 259,
    STATEVAR = 260,
    TMVAR = 261,
    TM = 262,
    EQ = 263,
    GEQ = 264,
    LEQ = 265,
    ASSIGN = 266,
    END = 267,
    MODE = 268,
    INIT = 269,
    BELONGSTO = 270,
    POLYODE1 = 271,
    POLYODE2 = 272,
    POLYODE3 = 273,
    VISUALIZE = 274,
    PARAAGGREG = 275,
    INTAGGREG = 276,
    TMAGGREG = 277,
    OUTPUT = 278,
    NOOUTPUT = 279,
    CONTINUOUS = 280,
    HYBRID = 281,
    SETTING = 282,
    FIXEDST = 283,
    FIXEDORD = 284,
    ADAPTIVEST = 285,
    ADAPTIVEORD = 286,
    ORDER = 287,
    MIN = 288,
    MAX = 289,
    REMEST = 290,
    INTERVAL = 291,
    OCTAGON = 292,
    GRID = 293,
    PLOT = 294,
    QRPRECOND = 295,
    IDPRECOND = 296,
    TIME = 297,
    MODES = 298,
    JUMPS = 299,
    INV = 300,
    GUARD = 301,
    RESET = 302,
    START = 303,
    MAXJMPS = 304,
    PRINTON = 305,
    PRINTOFF = 306,
    UNSAFESET = 307,
    CONTINUOUSFLOW = 308,
    HYBRIDFLOW = 309,
    TAYLOR_PICARD = 310,
    TAYLOR_REMAINDER = 311,
    TAYLOR_POLYNOMIAL = 312,
    NONPOLY_CENTER = 313,
    EXP = 314,
    SIN = 315,
    COS = 316,
    LOG = 317,
    SQRT = 318,
    NPODE_TAYLOR = 319,
    CUTOFF = 320,
    PRECISION = 321,
    GNUPLOT = 322,
    MATLAB = 323,
    COMPUTATIONPATHS = 324,
    LTI_ODE = 325,
    LTV_ODE = 326,
    PAR = 327,
    UNC = 328,
    UNIVARIATE_POLY = 329,
    TIME_INV = 330,
    TIME_VAR = 331,
    STEP = 332,
    TRUE = 333,
    FALSE = 334,
    LINEARCONTINUOUSFLOW = 335,
    uminus = 336
  };
#endif

/* Value type.  */
#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED

union YYSTYPE
{
#line 62 "modelParser.y" /* yacc.c:355  */

	double dblVal;
	int intVal;
	std::string *identifier;
	std::vector<flowstar::Interval> *intVec;
	std::vector<int> *iVec;
	std::vector<double> *dVec;
	std::vector<flowstar::Monomial> *monoVec;
	std::vector<flowstar::Polynomial> *polyVec;
	flowstar::Monomial *mono;
	flowstar::Polynomial *poly;
	flowstar::TaylorModelVec *tmVec;
	flowstar::Matrix *mat;
	std::vector<std::vector<double> > *dVecVec;
	std::vector<flowstar::PolynomialConstraint> *vecConstraints;
	flowstar::ResetMap *resetMap;
	flowstar::Flowpipe *pFlowpipe;
	std::vector<flowstar::Flowpipe> *pVecFlowpipe;
	flowstar::TaylorModel *ptm;
	flowstar::Interval *pint;
	std::vector<std::string> *strVec;
	flowstar::TreeNode *pNode;
	flowstar::UnivariatePolynomial *pUpoly;
	LTI_Term *p_LTI_Term;
	LTV_Term *p_LTV_Term;
	ODE_String *p_ODE_String;

#line 276 "modelParser.tab.c" /* yacc.c:355  */
};

typedef union YYSTYPE YYSTYPE;
# define YYSTYPE_IS_TRIVIAL 1
# define YYSTYPE_IS_DECLARED 1
#endif


extern YYSTYPE yylval;

int yyparse (void);

#endif /* !YY_YY_MODELPARSER_TAB_H_INCLUDED  */

/* Copy the second part of user declarations.  */

#line 293 "modelParser.tab.c" /* yacc.c:358  */

#ifdef short
# undef short
#endif

#ifdef YYTYPE_UINT8
typedef YYTYPE_UINT8 yytype_uint8;
#else
typedef unsigned char yytype_uint8;
#endif

#ifdef YYTYPE_INT8
typedef YYTYPE_INT8 yytype_int8;
#else
typedef signed char yytype_int8;
#endif

#ifdef YYTYPE_UINT16
typedef YYTYPE_UINT16 yytype_uint16;
#else
typedef unsigned short int yytype_uint16;
#endif

#ifdef YYTYPE_INT16
typedef YYTYPE_INT16 yytype_int16;
#else
typedef short int yytype_int16;
#endif

#ifndef YYSIZE_T
# ifdef __SIZE_TYPE__
#  define YYSIZE_T __SIZE_TYPE__
# elif defined size_t
#  define YYSIZE_T size_t
# elif ! defined YYSIZE_T
#  include <stddef.h> /* INFRINGES ON USER NAME SPACE */
#  define YYSIZE_T size_t
# else
#  define YYSIZE_T unsigned int
# endif
#endif

#define YYSIZE_MAXIMUM ((YYSIZE_T) -1)

#ifndef YY_
# if defined YYENABLE_NLS && YYENABLE_NLS
#  if ENABLE_NLS
#   include <libintl.h> /* INFRINGES ON USER NAME SPACE */
#   define YY_(Msgid) dgettext ("bison-runtime", Msgid)
#  endif
# endif
# ifndef YY_
#  define YY_(Msgid) Msgid
# endif
#endif

#ifndef YY_ATTRIBUTE
# if (defined __GNUC__                                               \
      && (2 < __GNUC__ || (__GNUC__ == 2 && 96 <= __GNUC_MINOR__)))  \
     || defined __SUNPRO_C && 0x5110 <= __SUNPRO_C
#  define YY_ATTRIBUTE(Spec) __attribute__(Spec)
# else
#  define YY_ATTRIBUTE(Spec) /* empty */
# endif
#endif

#ifndef YY_ATTRIBUTE_PURE
# define YY_ATTRIBUTE_PURE   YY_ATTRIBUTE ((__pure__))
#endif

#ifndef YY_ATTRIBUTE_UNUSED
# define YY_ATTRIBUTE_UNUSED YY_ATTRIBUTE ((__unused__))
#endif

#if !defined _Noreturn \
     && (!defined __STDC_VERSION__ || __STDC_VERSION__ < 201112)
# if defined _MSC_VER && 1200 <= _MSC_VER
#  define _Noreturn __declspec (noreturn)
# else
#  define _Noreturn YY_ATTRIBUTE ((__noreturn__))
# endif
#endif

/* Suppress unused-variable warnings by "using" E.  */
#if ! defined lint || defined __GNUC__
# define YYUSE(E) ((void) (E))
#else
# define YYUSE(E) /* empty */
#endif

#if defined __GNUC__ && 407 <= __GNUC__ * 100 + __GNUC_MINOR__
/* Suppress an incorrect diagnostic about yylval being uninitialized.  */
# define YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN \
    _Pragma ("GCC diagnostic push") \
    _Pragma ("GCC diagnostic ignored \"-Wuninitialized\"")\
    _Pragma ("GCC diagnostic ignored \"-Wmaybe-uninitialized\"")
# define YY_IGNORE_MAYBE_UNINITIALIZED_END \
    _Pragma ("GCC diagnostic pop")
#else
# define YY_INITIAL_VALUE(Value) Value
#endif
#ifndef YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
# define YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
# define YY_IGNORE_MAYBE_UNINITIALIZED_END
#endif
#ifndef YY_INITIAL_VALUE
# define YY_INITIAL_VALUE(Value) /* Nothing. */
#endif


#if ! defined yyoverflow || YYERROR_VERBOSE

/* The parser invokes alloca or malloc; define the necessary symbols.  */

# ifdef YYSTACK_USE_ALLOCA
#  if YYSTACK_USE_ALLOCA
#   ifdef __GNUC__
#    define YYSTACK_ALLOC __builtin_alloca
#   elif defined __BUILTIN_VA_ARG_INCR
#    include <alloca.h> /* INFRINGES ON USER NAME SPACE */
#   elif defined _AIX
#    define YYSTACK_ALLOC __alloca
#   elif defined _MSC_VER
#    include <malloc.h> /* INFRINGES ON USER NAME SPACE */
#    define alloca _alloca
#   else
#    define YYSTACK_ALLOC alloca
#    if ! defined _ALLOCA_H && ! defined EXIT_SUCCESS
#     include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
      /* Use EXIT_SUCCESS as a witness for stdlib.h.  */
#     ifndef EXIT_SUCCESS
#      define EXIT_SUCCESS 0
#     endif
#    endif
#   endif
#  endif
# endif

# ifdef YYSTACK_ALLOC
   /* Pacify GCC's 'empty if-body' warning.  */
#  define YYSTACK_FREE(Ptr) do { /* empty */; } while (0)
#  ifndef YYSTACK_ALLOC_MAXIMUM
    /* The OS might guarantee only one guard page at the bottom of the stack,
       and a page size can be as small as 4096 bytes.  So we cannot safely
       invoke alloca (N) if N exceeds 4096.  Use a slightly smaller number
       to allow for a few compiler-allocated temporary stack slots.  */
#   define YYSTACK_ALLOC_MAXIMUM 4032 /* reasonable circa 2006 */
#  endif
# else
#  define YYSTACK_ALLOC YYMALLOC
#  define YYSTACK_FREE YYFREE
#  ifndef YYSTACK_ALLOC_MAXIMUM
#   define YYSTACK_ALLOC_MAXIMUM YYSIZE_MAXIMUM
#  endif
#  if (defined __cplusplus && ! defined EXIT_SUCCESS \
       && ! ((defined YYMALLOC || defined malloc) \
             && (defined YYFREE || defined free)))
#   include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
#   ifndef EXIT_SUCCESS
#    define EXIT_SUCCESS 0
#   endif
#  endif
#  ifndef YYMALLOC
#   define YYMALLOC malloc
#   if ! defined malloc && ! defined EXIT_SUCCESS
void *malloc (YYSIZE_T); /* INFRINGES ON USER NAME SPACE */
#   endif
#  endif
#  ifndef YYFREE
#   define YYFREE free
#   if ! defined free && ! defined EXIT_SUCCESS
void free (void *); /* INFRINGES ON USER NAME SPACE */
#   endif
#  endif
# endif
#endif /* ! defined yyoverflow || YYERROR_VERBOSE */


#if (! defined yyoverflow \
     && (! defined __cplusplus \
         || (defined YYSTYPE_IS_TRIVIAL && YYSTYPE_IS_TRIVIAL)))

/* A type that is properly aligned for any stack member.  */
union yyalloc
{
  yytype_int16 yyss_alloc;
  YYSTYPE yyvs_alloc;
};

/* The size of the maximum gap between one aligned stack and the next.  */
# define YYSTACK_GAP_MAXIMUM (sizeof (union yyalloc) - 1)

/* The size of an array large to enough to hold all stacks, each with
   N elements.  */
# define YYSTACK_BYTES(N) \
     ((N) * (sizeof (yytype_int16) + sizeof (YYSTYPE)) \
      + YYSTACK_GAP_MAXIMUM)

# define YYCOPY_NEEDED 1

/* Relocate STACK from its old location to the new one.  The
   local variables YYSIZE and YYSTACKSIZE give the old and new number of
   elements in the stack, and YYPTR gives the new location of the
   stack.  Advance YYPTR to a properly aligned location for the next
   stack.  */
# define YYSTACK_RELOCATE(Stack_alloc, Stack)                           \
    do                                                                  \
      {                                                                 \
        YYSIZE_T yynewbytes;                                            \
        YYCOPY (&yyptr->Stack_alloc, Stack, yysize);                    \
        Stack = &yyptr->Stack_alloc;                                    \
        yynewbytes = yystacksize * sizeof (*Stack) + YYSTACK_GAP_MAXIMUM; \
        yyptr += yynewbytes / sizeof (*yyptr);                          \
      }                                                                 \
    while (0)

#endif

#if defined YYCOPY_NEEDED && YYCOPY_NEEDED
/* Copy COUNT objects from SRC to DST.  The source and destination do
   not overlap.  */
# ifndef YYCOPY
#  if defined __GNUC__ && 1 < __GNUC__
#   define YYCOPY(Dst, Src, Count) \
      __builtin_memcpy (Dst, Src, (Count) * sizeof (*(Src)))
#  else
#   define YYCOPY(Dst, Src, Count)              \
      do                                        \
        {                                       \
          YYSIZE_T yyi;                         \
          for (yyi = 0; yyi < (Count); yyi++)   \
            (Dst)[yyi] = (Src)[yyi];            \
        }                                       \
      while (0)
#  endif
# endif
#endif /* !YYCOPY_NEEDED */

/* YYFINAL -- State number of the termination state.  */
#define YYFINAL  20
/* YYLAST -- Last index in YYTABLE.  */
#define YYLAST   1641

/* YYNTOKENS -- Number of terminals.  */
#define YYNTOKENS  98
/* YYNNTS -- Number of nonterminals.  */
#define YYNNTS  80
/* YYNRULES -- Number of rules.  */
#define YYNRULES  341
/* YYNSTATES -- Number of states.  */
#define YYNSTATES  1298

/* YYTRANSLATE[YYX] -- Symbol number corresponding to YYX as returned
   by yylex, with out-of-bounds checking.  */
#define YYUNDEFTOK  2
#define YYMAXUTOK   336

#define YYTRANSLATE(YYX)                                                \
  ((unsigned int) (YYX) <= YYMAXUTOK ? yytranslate[YYX] : YYUNDEFTOK)

/* YYTRANSLATE[TOKEN-NUM] -- Symbol number corresponding to TOKEN-NUM
   as returned by yylex, without out-of-bounds checking.  */
static const yytype_uint8 yytranslate[] =
{
       0,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,    96,
      90,    94,    83,    81,    91,    82,     2,    84,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,    97,    89,
       2,     2,    95,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,    92,     2,    93,    86,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,    87,     2,    88,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     1,     2,     3,     4,
       5,     6,     7,     8,     9,    10,    11,    12,    13,    14,
      15,    16,    17,    18,    19,    20,    21,    22,    23,    24,
      25,    26,    27,    28,    29,    30,    31,    32,    33,    34,
      35,    36,    37,    38,    39,    40,    41,    42,    43,    44,
      45,    46,    47,    48,    49,    50,    51,    52,    53,    54,
      55,    56,    57,    58,    59,    60,    61,    62,    63,    64,
      65,    66,    67,    68,    69,    70,    71,    72,    73,    74,
      75,    76,    77,    78,    79,    80,    85
};

#if YYDEBUG
  /* YYRLINE[YYN] -- Source line where rule number YYN was defined.  */
static const yytype_uint16 yyrline[] =
{
       0,   166,   166,   267,   393,   494,   622,   664,   683,   703,
     746,   780,   788,   795,   801,   807,   814,   821,   831,   841,
     851,   860,   865,   870,   875,   880,   886,   892,   897,   916,
     937,   950,   964,   977,   993,  1019,  1046,  1071,  1097,  1101,
    1106,  1141,  1175,  1181,  1188,  1195,  1200,  1216,  1226,  1242,
    1261,  1283,  1302,  1333,  1367,  1404,  1455,  1698,  1720,  1742,
    1764,  1786,  1806,  1826,  1850,  1874,  1896,  1918,  1940,  1962,
    1982,  2002,  2026,  2051,  2062,  2074,  2109,  2128,  2138,  2148,
    2158,  2168,  2178,  2188,  2198,  2208,  2218,  2228,  2238,  2251,
    2255,  2259,  2271,  2287,  2292,  2297,  2302,  2318,  2330,  2350,
    2375,  2402,  2443,  2447,  2478,  2502,  2507,  2534,  2555,  2571,
    2577,  2582,  2623,  2640,  2660,  2665,  2679,  2696,  2701,  2726,
    2753,  2784,  2815,  2820,  2853,  2886,  2890,  2935,  2989,  3047,
    3120,  3173,  3240,  3257,  3274,  3298,  3325,  3342,  3366,  3372,
    3379,  3429,  3479,  3531,  3581,  3631,  3684,  3692,  3700,  3709,
    3719,  3731,  3736,  3770,  3810,  3815,  3828,  3848,  3875,  3886,
    3936,  3995,  4020,  4038,  4060,  4074,  4094,  4109,  4113,  4117,
    4121,  4127,  4164,  4185,  4222,  4238,  4243,  4248,  4253,  4258,
    4263,  4270,  4307,  4328,  4353,  4380,  4388,  4396,  4401,  4409,
    4427,  4434,  4462,  4480,  4488,  4496,  4501,  4509,  4527,  4534,
    4576,  4583,  4593,  4601,  4609,  4614,  4622,  4640,  4647,  4689,
    4700,  4708,  4716,  4721,  4729,  4747,  4754,  4796,  4808,  4835,
    4880,  4888,  4896,  4901,  4909,  4927,  4934,  4992,  5008,  5044,
    5051,  5058,  5074,  5079,  5098,  5107,  5116,  5125,  5134,  5143,
    5190,  5197,  5220,  5254,  5261,  5268,  5284,  5289,  5308,  5317,
    5326,  5335,  5344,  5353,  5409,  5415,  5436,  5463,  5471,  5479,
    5489,  5494,  5507,  5516,  5525,  5534,  5543,  5552,  5562,  5568,
    5586,  5614,  5625,  5636,  5647,  5658,  5669,  5680,  5691,  5702,
    5713,  5724,  5736,  5746,  5774,  5793,  5827,  5844,  5861,  5878,
    5889,  5906,  5922,  5938,  5954,  5970,  5986,  6003,  6018,  6038,
    6057,  6196,  6216,  6236,  6256,  6278,  6329,  6380,  6431,  6436,
    6452,  6464,  6476,  6488,  6502,  6535,  6568,  6601,  6606,  6636,
    6656,  6676,  6696,  6719,  6769,  6819,  6831,  6843,  6855,  6867,
    6883,  6915,  6947,  6962,  6970,  6978,  6983,  6991,  7008,  7015,
    7031,  7037
};
#endif

#if YYDEBUG || YYERROR_VERBOSE || 0
/* YYTNAME[SYMBOL-NUM] -- String name of the symbol SYMBOL-NUM.
   First, the terminals, then, starting at YYNTOKENS, nonterminals.  */
static const char *const yytname[] =
{
  "$end", "error", "$undefined", "NUM", "IDENT", "STATEVAR", "TMVAR",
  "TM", "EQ", "GEQ", "LEQ", "ASSIGN", "END", "MODE", "INIT", "BELONGSTO",
  "POLYODE1", "POLYODE2", "POLYODE3", "VISUALIZE", "PARAAGGREG",
  "INTAGGREG", "TMAGGREG", "OUTPUT", "NOOUTPUT", "CONTINUOUS", "HYBRID",
  "SETTING", "FIXEDST", "FIXEDORD", "ADAPTIVEST", "ADAPTIVEORD", "ORDER",
  "MIN", "MAX", "REMEST", "INTERVAL", "OCTAGON", "GRID", "PLOT",
  "QRPRECOND", "IDPRECOND", "TIME", "MODES", "JUMPS", "INV", "GUARD",
  "RESET", "START", "MAXJMPS", "PRINTON", "PRINTOFF", "UNSAFESET",
  "CONTINUOUSFLOW", "HYBRIDFLOW", "TAYLOR_PICARD", "TAYLOR_REMAINDER",
  "TAYLOR_POLYNOMIAL", "NONPOLY_CENTER", "EXP", "SIN", "COS", "LOG",
  "SQRT", "NPODE_TAYLOR", "CUTOFF", "PRECISION", "GNUPLOT", "MATLAB",
  "COMPUTATIONPATHS", "LTI_ODE", "LTV_ODE", "PAR", "UNC",
  "UNIVARIATE_POLY", "TIME_INV", "TIME_VAR", "STEP", "TRUE", "FALSE",
  "LINEARCONTINUOUSFLOW", "'+'", "'-'", "'*'", "'/'", "uminus", "'^'",
  "'{'", "'}'", "';'", "'('", "','", "'['", "']'", "')'", "'>'", "'\\''",
  "':'", "$accept", "model", "output_env", "unsafe_continuous_env",
  "unsafe_hybrid_env", "range_contracted", "init_flowpipes",
  "linear_flowpipes", "continuous_flowpipes", "initial_flowpipes",
  "linear_continuous_flowpipes", "modeDecls", "hybrid_flowpipes",
  "computation_paths", "computation_path", "print", "unsafe_continuous",
  "unsafe_hybrid", "hybrid_constraints", "polynomial_constraints",
  "continuous", "hybrid", "hybrid_init", "modes", "local_setting",
  "parameters", "jumps", "reset", "real_valued_vectors",
  "real_valued_vector", "vector_components", "stateVarDecls",
  "stateIdDeclList", "parDecls", "parDeclList", "TIParDeclList",
  "TVParDeclList", "settings", "remainder_estimation", "remainders",
  "orders", "precondition", "plotting", "init", "set_of_intervals",
  "tmVarDecls", "tmIdDeclList", "tmVarDecls2", "tmIdDeclList2",
  "taylor_model", "taylor_model_domain", "intervals", "ode", "npode",
  "lti_env", "lti_ode", "lti_ode_hybrid", "ltv_env", "ltv_ode",
  "ltv_ode_hybrid", "polynomial", "ODEpolynomial", "constraint_polynomial",
  "reset_polynomial", "interval_taylor_model", "interval_polynomial",
  "non_polynomial_rhs_picard", "non_polynomial_rhs_remainder",
  "non_polynomial_rhs_no_remainder", "non_polynomial_rhs_string",
  "non_polynomial_rhs_center", "lti_ode_rhs", "lti_ode_rhs_term",
  "lti_ode_hybrid_rhs", "lti_ode_hybrid_rhs_term", "ltv_ode_rhs",
  "ltv_ode_rhs_term", "ltv_ode_hybrid_rhs", "ltv_ode_hybrid_rhs_term",
  "univariate_polynomial", YY_NULLPTR
};
#endif

# ifdef YYPRINT
/* YYTOKNUM[NUM] -- (External) token number corresponding to the
   (internal) symbol number NUM (which must be that of a token).  */
static const yytype_uint16 yytoknum[] =
{
       0,   256,   257,   258,   259,   260,   261,   262,   263,   264,
     265,   266,   267,   268,   269,   270,   271,   272,   273,   274,
     275,   276,   277,   278,   279,   280,   281,   282,   283,   284,
     285,   286,   287,   288,   289,   290,   291,   292,   293,   294,
     295,   296,   297,   298,   299,   300,   301,   302,   303,   304,
     305,   306,   307,   308,   309,   310,   311,   312,   313,   314,
     315,   316,   317,   318,   319,   320,   321,   322,   323,   324,
     325,   326,   327,   328,   329,   330,   331,   332,   333,   334,
     335,    43,    45,    42,    47,   336,    94,   123,   125,    59,
      40,    44,    91,    93,    41,    62,    39,    58
};
# endif

#define YYPACT_NINF -1092

#define yypact_value_is_default(Yystate) \
  (!!((Yystate) == (-1092)))

#define YYTABLE_NINF -220

#define yytable_value_is_error(Yytable_value) \
  0

  /* YYPACT[STATE-NUM] -- Index in YYTABLE of the portion describing
     STATE-NUM.  */
static const yytype_int16 yypact[] =
{
     579,    44,   -15,    14,   191,   246,   264,   274,   286,   259,
     477, -1092,   216,   399,   399,   190,   201,   237,    82,    57,
   -1092,   341,   535,  1057,    26,     0,   336,   331,    27,   385,
     168, -1092,   393,   403,   405,   411,   419,   190,   190,   464,
     927, -1092,   431,   471,   493,   495,   502,   201,   201,   472,
     935, -1092,   516,   530,   543,   548,   592,   237,   237,   521,
     943, -1092, -1092,   598,   604,   608,   612,   614,    82,    82,
     526,   951, -1092, -1092,    57,    57,   666,   959,   563,   721,
     723,   729,   734,   736,   750,   636,   655,   752,   773, -1092,
     428,   670,   695,   761,   738,   705,   772,   190,   190,   190,
     190,   190,   732,   589,   735,   190,   190,   190,   190,   821,
   -1092,   201,   201,   201,   201,   201,   742,   603,   765,   201,
     201,   201,   201,   838, -1092,   237,   237,   237,   237,   237,
     753,   609,   767,   237,   237,   237,   237,   840, -1092,    82,
      82,    82,    82,    82,   768,   647,   792,    82,    82,    82,
      82,   866, -1092,   803,   513,   800,    57,    57,    57,   890,
   -1092,   872,   815,   817,   915,   832,   854,   939,   860,   954,
     901,   930,   886, -1092, -1092,   172,   977,   905,   909, -1092,
   -1092,   172,   916,   653,   662,   668,   683,   697, -1092,   974,
     129,   129,   732,   732, -1092,   703,   712,   719,   733,   739,
   -1092,   985,   136,   136,   742,   742, -1092,   748,   754,   763,
     769,   778, -1092,  1004,   433,   433,   753,   753, -1092,   784,
     798,   804,   813,   819, -1092,  1017,   463,   463,   768,   768,
   -1092, -1092,  1019,   -18,   -18,   803, -1092,  1027,  1010,  1024,
     945,  1034,  1040,  1028,  1026, -1092,    58,   153,  1087,  1105,
   -1092,  1117,  1035,   175,  1113,    71,   172, -1092,  1074,   172,
   -1092, -1092, -1092, -1092, -1092,  1031, -1092, -1092, -1092, -1092,
   -1092,  1033, -1092, -1092, -1092, -1092, -1092,  1036, -1092, -1092,
   -1092, -1092, -1092,  1037,  1038,  1039, -1092, -1092,  1121, -1092,
   -1092,  1124,  1129,   436,   461, -1092,  1130,    35,  1069,   204,
    1093,  1103, -1092, -1092,  1049,  1135,  1131, -1092,   175,    98,
    1137,  1092, -1092, -1092, -1092, -1092, -1092,  1055, -1092, -1092,
    1056,    35, -1092,  1052,  1122,  1142, -1092,  1125,   591,  1144,
   -1092, -1092,   284, -1092,   284,   533,  1146,  1147,   547, -1092,
    1148,  1064,  1066, -1092,   175,  1151,  1090,  1070,   181,  1067,
    1152, -1092,  1154,  1073,  1108,    35,  1076,   873,   708,   806,
    1048,  1071,   284,   284,   284,  1161,  1132,  1075,  1078,  1081,
    1082,  1083,  1084,  1085, -1092,   584, -1092,  1086,   175,  1170,
    1110,  1089,  1123,  1175, -1092, -1092,  1173,  1094,    -9, -1092,
   -1092, -1092, -1092, -1092, -1092, -1092,  1065,   507,   507,  1076,
   -1092,   167,   836,  1149,  1177, -1092, -1092,  1179,   855,  1021,
    1097,  1098,  1099,  1100,  1101,  1102,   213,  1150,  1106,  1107,
    1187,  1188,  1109,  1111,  1193,  1112,  1173,  1114,  1116,  1115,
    1118, -1092,  1194, -1092, -1092,   436,  1197,  1119,   193,   202,
     228,  1120,   230,  1126,  1127,  1128,  1199,  1133,   235,  1134,
    1200,  1202, -1092, -1092,  1207,   855,  1021, -1092,  1136,  1168,
    1138,  1139,  1141,   309,  1188,  1209, -1092,  1140,  1211,  1011,
    1112,  1213,  1143,  1215,  1217,  1145,   123,   242,  1153,  1156,
    1155,  1205,  1210,  1212,  1157,  1158,  1218,  1213,  1225,  1219,
    1159,  1213,  1160,  1225,  1220,  1162,  1164,   326,   327,   332,
    1165,   338,  1169,  1171,  1231,  1163, -1092,  1174,  1173,  1176,
   -1092,   352,  1167,  1232,  1229,  1234,  1211, -1092,  1013, -1092,
     618,  1213,  1172,  1178,  1180, -1092,  1235,   367,  1181,  1198,
   -1092,  1237,  1182,  1183,  1186, -1092,  1238,  1189,   716, -1092,
     720,  1190,  1240,   783,  1225,   869,  1191,  1241,  1192,  1242,
    1248,  1250,  1195,  1252,  1253,  1260,  1254,   371,  1231,   220,
   -1092,  1112,  1173, -1092,  1196, -1092,    86,    32,   449,  1234,
   -1092,  1261,  1276,   884, -1092, -1092,  1280,  1201,  1221,  1281,
    1251,  1284,   373,    89,   187,   187,   187,   374,    93,   187,
     -23,  1204,  1285,   187,   163,   122,   899,  1206,   187,    83,
   -1092,  1208,  1214,  1216, -1092,  1222,  1223,  1224,  1226,  1227,
    1254,  1244,   375,  1228,   224,  1015,  1112,  1230, -1092, -1092,
      86,    86,  1289,   527,    86,  1233,  1279, -1092, -1092,  1236,
     449,  1239, -1092,  1282,  1243,  1245,  1294,  1203,   914,   377,
    1132,  1288, -1092, -1092,    89,    89,  1296,   632, -1092,  1247,
    1246, -1092,  1300,  1255,  1256,  1291, -1092, -1092,  1249,  1257,
    1258,  1259,  1262,    93,    93,  1303,   677,  1263,  1266, -1092,
   -1092, -1092,  1267,  1271, -1092,    46,  1304,  1023, -1092,   378,
   -1092,  1269, -1092,  1270, -1092,    72,    57,  1025, -1092,   380,
     187,   187,   187,   381,   187,   187,   187, -1092,   610,  1272,
    1273,  1264, -1092,  1274, -1092,  1022,  1268,  1275,   882,  1277,
     100,    86,    86,  1312,   967,  1314,  1265, -1092,  1278,  1313,
    1283,  1315,  1317,  1298,  1318,  1302,  1319,  1286,  1281,   836,
    1287,  1290,   888,  1292,    89,    89,    89,  1324,   382, -1092,
   -1092,  1325,  1307, -1092, -1092,  1293,    93,    93,    93,    93,
      93,  1295,   828,  1297,    93,    93,    93,    93,  1327, -1092,
    1225,   383,   384, -1092,  1328, -1092,  1299,    46,    46,  1305,
    1225,   386, -1092,   388, -1092, -1092,   897,    72,    72,  1322,
    1301,  1306,  1308,  1326,  1309,  1310,  1311,   611,  1316,  1320,
    1321,  1323,  1329,  1330,   646, -1092,  1331, -1092, -1092,  1334,
      86, -1092,  1338,  1339,   960,   960,  1275, -1092,   109,  1332,
    1342, -1092,  1346,  1333,  1335,  1313,  1336,  1337,  1343, -1092,
    1362,  1340,  1341,   969,   436,   187, -1092,  1366,   981,   981,
    1290, -1092, -1092,   389,   188,  1367,  1344,   187,   834,   843,
     852,   858,   867, -1092,  1369,   476,   476,  1295,  1295, -1092,
     982, -1092, -1092, -1092,  1370, -1092, -1092,  1225,   983, -1092,
     390, -1092,  1347, -1092, -1092,  1345, -1092, -1092, -1092,  1348,
   -1092, -1092, -1092,  1375,   379,  1351,  1352,   392, -1092, -1092,
    1376, -1092, -1092, -1092, -1092, -1092, -1092, -1092,  1353,  1354,
    1355,  1356,  1357,  1358,   394, -1092, -1092,  1359,  1360,  1379,
    1381,  1363, -1092,  1364,  1368,  1211,  1371,  1361, -1092,  1382,
      35,  1349,  1383,  1384,  1365,  1372,  1373,  1374, -1092,   355,
    1388,  1377, -1092, -1092, -1092, -1092, -1092,  1378,  1385,  1380,
     984,  1387, -1092,  1389,   187,   187, -1092, -1092,  1281,  1386,
    1391, -1092,  1194, -1092,   396,   397,   402,   404,   406,   408,
   -1092, -1092, -1092, -1092, -1092, -1092,  1393,  1390,   409, -1092,
    1392,  1394,  1395,  1397,  1398,  1396,  1234,  1211,  1399,  1400,
   -1092,  1402, -1092,  1401,  1412,   413, -1092, -1092, -1092, -1092,
     355,   355,   973,  1403, -1092, -1092, -1092,  1350,  1404, -1092,
   -1092,  1407,  1408,   988,  1406,   415,   989,  1405,  1414,  1415,
    1417,  1409,  1418,  1410,  1419,   417,   418,   425,   427,   430,
     432,  1413,  1411,  1420,  1416,  1422, -1092,  1421, -1092,  1313,
     434,  1234,  1423, -1092,    35,  1425,  1424,  1427,  1281,  1426,
     903,   147,   355,   355,  1428,  1444,   435,  1449, -1092,   437,
   -1092, -1092, -1092,  1429,  1430,  1281, -1092,  1431,  1432,  1435,
    1436,  1458,  1437,  1460,  1438,  1433,  1439,  1441,  1442,  1452,
    1454,  1453,  1465,  1440,   438,  1443, -1092,  1445,  1447, -1092,
     442,  1313, -1092,  1467,  1281,  1473,   990,   355, -1092,  1474,
     999,   999,  1426, -1092,  1446, -1092, -1092,   443, -1092,  1448,
    1466,   995, -1092, -1092, -1092, -1092,   185, -1092,   128, -1092,
    1450,  1451,  1455,  1456,  1457,  1459,  1434,  1461,  1462,  1465,
     444, -1092,  1211,  1464, -1092,  1468,  1463,   996,  1469,  1475,
    1470, -1092, -1092,  1478,  1498,  1471,   227,   244,   253,   262,
    1472, -1092,    48,  1499,  1030, -1092,   265, -1092,    94,    57,
    1032, -1092,   272, -1092, -1092, -1092, -1092, -1092, -1092,  1476,
    1173, -1092,  1477,   445,  1211, -1092,  1500,  1479,  1501,  1504,
    1510,  1480,  1481,  1482,  1483,  1484,  1485,  1486,  1511, -1092,
    1487,    48,    48,  1488, -1092,   912,    94,    94,  1489,   281,
     301,   317,   321,   335,   342, -1092, -1092,   446, -1092,  1509,
   -1092,   448,    35,  1492,    35,  1493,  1490, -1092, -1092,  1494,
   -1092, -1092, -1092, -1092, -1092,  1523, -1092, -1092, -1092,  1496,
   -1092, -1092, -1092,  1497,  1502,  1503,  1505,  1506,  1507,   345,
    1325, -1092, -1092, -1092,  1525, -1092,  1527, -1092,  1281,  1491,
    1528, -1092, -1092, -1092, -1092, -1092, -1092,  1513,   451,  1514,
      35,  1000,  1515, -1092,  1495, -1092,  1538, -1092,  1508,  1541,
   -1092,    35, -1092, -1092,   452, -1092,  1512,  1095,  1520,  1516,
   -1092,   361, -1092, -1092, -1092,   361,   361,   980,   -54,  1518,
     918,   154,   361,   361,  1544, -1092,  1545, -1092,   361, -1092,
    1549,  1006,  1006,  1518, -1092,  1517,   398,  1519,  1550,  1554,
   -1092,  1551, -1092,  1521,  1522,  1561, -1092, -1092
};

  /* YYDEFACT[STATE-NUM] -- Default reduction number in state STATE-NUM.
     Performed when YYTABLE does not specify something else to do.  Zero
     means the default is an error.  */
static const yytype_uint16 yydefact[] =
{
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,   116,   114,     0,     0,     0,     0,     0,     0,     0,
       1,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,   241,     0,     0,     0,     0,     0,     0,     0,     0,
       0,   255,     0,     0,     0,     0,     0,     0,     0,     0,
       0,   269,     0,     0,     0,     0,     0,     0,     0,     0,
       0,   300,   298,     0,     0,     0,     0,     0,     0,     0,
       0,     0,   341,   339,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,   115,
       2,     0,     0,     0,     4,     0,     0,     0,     0,     0,
       0,     0,   240,     0,     0,     0,     0,     0,     0,     0,
      12,     0,     0,     0,     0,     0,   254,     0,     0,     0,
       0,     0,     0,     0,    13,     0,     0,     0,     0,     0,
     268,     0,     0,     0,     0,     0,     0,     0,    14,     0,
       0,     0,     0,     0,   297,     0,     0,     0,     0,     0,
       0,     0,    15,   338,     0,     0,     0,     0,     0,     0,
      16,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     3,    21,     0,     0,     0,     0,     5,
      22,     0,     0,     0,     0,     0,     0,     0,   232,     0,
     229,   230,   231,   233,   239,     0,     0,     0,     0,     0,
     246,     0,   243,   244,   245,   247,   253,     0,     0,     0,
       0,     0,   260,     0,   257,   258,   259,   261,   267,     0,
       0,     0,     0,     0,   289,     0,   286,   287,   288,   290,
     296,   335,     0,   333,   334,   336,   337,     0,     0,     0,
       0,     0,     0,     0,     0,    41,     0,     0,     0,     0,
      56,     0,     0,     0,     0,     0,     0,    47,     0,     0,
     234,   235,   236,   237,   238,     0,   248,   249,   250,   251,
     252,     0,   262,   263,   264,   265,   266,     0,   291,   292,
     293,   294,   295,     0,     0,     0,   140,   141,     0,   143,
     144,     0,     0,     0,     0,    39,     0,     0,     0,     0,
       0,     0,    42,    43,     0,     0,     0,   117,     0,     0,
       0,     0,   242,   256,   270,   299,   340,     0,   142,   145,
       0,     0,    38,     0,     0,     0,    20,     0,     0,     0,
     209,   208,     0,    44,     0,     0,     0,     0,     0,   119,
       0,     0,     0,    45,     0,     0,     0,     0,     0,     0,
       0,    17,     0,     0,     0,     0,   207,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,   118,     0,    56,     0,     0,     0,
       0,     0,     0,     0,    19,    18,     0,     0,     0,   204,
      50,    54,    49,    53,    48,    52,     0,   202,   203,   205,
     206,     0,     0,     0,   164,   164,   164,   166,   172,   182,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,   132,     0,   138,   139,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,   170,     0,     0,     0,
     180,   164,   164,   164,   166,   172,   182,    46,     0,     0,
       0,     0,     0,     0,     0,     0,   153,   151,     0,     0,
       0,   122,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,   122,   125,     0,
       0,   122,     0,   125,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,    56,     0,     0,     0,
      11,     0,     0,     0,     0,     0,     0,     7,     0,   121,
       0,   122,     0,     0,     0,   133,     0,     0,     0,     0,
     164,     0,     0,     0,     0,   166,     0,     0,     0,   124,
       0,     0,     0,     0,   125,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,    90,     0,     0,     0,
      56,     0,     0,    10,     0,   152,     0,     0,    25,     0,
       6,     0,     0,     0,    51,    55,     0,     0,     0,     0,
       0,     0,     0,     0,   162,   162,   162,     0,     0,   162,
       0,     0,     0,   162,     0,     0,     0,     0,   162,     0,
     164,     0,     0,     0,   166,     0,     0,     0,     0,     0,
      90,     0,     0,     0,     0,     0,     0,     0,   228,   226,
       0,     0,     0,     0,     0,     0,     0,    23,    24,     0,
      25,     0,   120,     0,     0,     0,     0,     0,     0,     0,
       0,     0,   201,   199,     0,     0,     0,   163,   162,     0,
     148,   158,   147,     0,     0,     0,   285,   283,     0,     0,
       0,     0,     0,     0,     0,     0,   165,     0,     0,   172,
     172,   123,     0,   309,   307,     0,     0,   171,   304,     0,
     182,     0,   182,     0,   324,     0,     0,   181,   322,     0,
     162,   162,   162,     0,   162,   162,   162,   102,     0,     0,
       0,     0,    35,     0,    37,     0,     0,   225,     0,     0,
       0,     0,     0,     0,     0,     0,     0,    29,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,   198,     0,     0,     0,     0,     0,     0,     0,    57,
     162,     0,     0,    58,    59,     0,     0,     0,     0,     0,
       0,   282,     0,     0,     0,     0,     0,     0,     0,    60,
     125,     0,     0,    61,     0,   303,     0,     0,     0,     0,
     125,     0,   182,     0,    62,   321,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,   105,     0,    34,    36,     0,
       0,   222,     0,     0,   220,   221,   223,   224,     0,     0,
       0,    28,     0,     0,     0,     0,     0,     0,     0,   137,
       0,     0,     0,     0,     0,   162,   195,     0,   193,   194,
     196,   197,   150,     0,     0,   146,     0,   162,     0,     0,
       0,     0,     0,   274,     0,   271,   272,   273,   275,   281,
       0,   168,   169,   305,     0,   301,   302,   125,     0,   177,
       0,   178,   325,   319,   320,     0,    65,    66,    67,     0,
      68,    69,    70,     0,     0,     0,     0,     0,    94,    95,
       0,    89,   164,   164,   164,   166,   174,   184,     0,     0,
       0,     0,     0,     0,     0,   105,    40,     0,     0,     0,
       0,     0,   156,   154,     0,     0,    26,     0,   135,     0,
       0,     0,     0,     0,     0,     0,     0,     0,   149,     0,
       0,     0,   276,   277,   278,   279,   280,     0,     0,     0,
       0,     0,   179,     0,   162,   162,    91,    96,     0,     0,
       0,    92,     0,    97,     0,     0,     0,     0,     0,     0,
     164,   164,   164,   166,   174,   184,     0,     0,     0,   227,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
     126,     0,   136,     0,     0,     0,    63,   200,   192,   191,
       0,     0,     0,     0,    64,   284,   172,   308,     0,   182,
     323,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,   160,     0,   155,     0,
       0,     0,     0,   134,     0,     0,     0,     0,     0,   190,
       0,     0,     0,     0,     0,     0,     0,     0,   182,     0,
      71,    72,   100,     0,     0,     0,    93,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,   227,     0,   159,     0,     0,    31,
       0,     0,   128,     0,     0,     0,     0,     0,   187,     0,
     185,   186,   188,   189,     0,   167,   306,     0,   175,     0,
       0,     0,    56,    56,    56,    56,     0,    56,     0,    56,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
     227,     8,     0,    27,    30,     0,     0,     0,     0,     0,
       0,   161,   176,     0,     0,     0,     0,     0,     0,     0,
     318,   316,     0,     0,   173,   313,     0,   331,     0,     0,
     183,   329,     0,    56,    56,    56,    56,    56,    56,     0,
     162,    73,     0,     0,     0,     9,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,   312,
       0,     0,     0,     0,   328,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,    56,   158,     0,    74,     0,
      33,     0,     0,     0,     0,     0,     0,    98,    99,     0,
      78,    80,    82,    84,   314,     0,   310,   311,    86,   332,
     326,   327,    88,     0,     0,     0,     0,     0,     0,     0,
       0,    75,    32,   127,     0,   130,     0,   157,     0,     0,
       0,    77,    79,    81,    83,    85,    87,     0,     0,     0,
       0,     0,   317,   330,     0,    76,     0,   131,     0,     0,
     108,     0,   101,   315,     0,   129,     0,     0,     0,     0,
     104,     0,   110,   217,   216,     0,     0,   107,     0,   215,
       0,     0,     0,     0,     0,   103,     0,   109,     0,   212,
       0,   210,   211,   213,   214,     0,     0,     0,     0,     0,
     111,     0,   113,     0,     0,     0,   106,   112
};

  /* YYPGOTO[NTERM-NUM].  */
static const yytype_int16 yypgoto[] =
{
   -1092, -1092,  -319, -1092, -1092,   698,   596,   260,  -447, -1092,
   -1092, -1092,   942, -1092,  1166,  -273,  -300,  1072, -1092,  -373,
   -1092, -1092,   304,   856,   816, -1092,   532, -1092, -1092, -1092,
   -1092,  1104, -1092,  1536, -1092,  -454,  -481,   279,   946,   628,
    -717,   846,  -287,  -567, -1092,  -382, -1092,  -980, -1092,   401,
    -564,  -640,  -396,  -441,  1184,  -649,   634,  1185,  -666,   637,
    -902,  -599,   315,  -565,  -509,  -551,   560,   510,   441,  -639,
     439, -1092,  -648, -1092, -1091, -1092,  -656, -1092,  -624,   -74
};

  /* YYDEFGOTO[NTERM-NUM].  */
static const yytype_int16 yydefgoto[] =
{
      -1,     9,   328,   173,   179,   629,   813,  1067,   469,   906,
    1113,    24,   463,   246,   247,   304,   174,   180,   309,   299,
      27,    29,  1108,   557,   609,   787,   894,  1254,  1268,  1277,
    1286,    10,    12,    93,   255,   520,   540,   253,   402,   476,
     638,   435,    25,   649,   650,   651,   467,   814,   903,   741,
     568,   652,   438,   442,   445,   446,   948,   449,   450,   949,
    1080,   647,   335,  1281,   515,   804,    40,    50,    60,   666,
      71,   677,   678,  1134,  1135,   687,   688,  1140,  1141,    77
};

  /* YYTABLE[YYPACT[STATE-NUM]] -- What to do in state STATE-NUM.  If
     positive, shift that token.  If negative, reduce the rule whose
     number is the opposite.  If YYTABLE_NINF, syntax error.  */
static const yytype_int16 yytable[] =
{
     153,   154,   348,   416,   425,   630,   321,   569,   738,   439,
     440,   823,   545,   501,   771,   623,   773,   982,   653,   654,
     761,   762,   667,   518,   751,   752,   672,   765,   354,   775,
      85,   683,    87,   538,  1275,   341,   388,   543,  1276,  1068,
     624,  1169,   324,   172,   470,   731,   732,   625,    11,   673,
     674,  1130,  1131,   668,    91,   497,   498,   499,   325,   326,
      72,    73,   245,   596,   669,   158,   427,   573,   159,   707,
     708,   377,    13,   714,   327,   306,   684,    88,  1029,  1030,
    1206,  1207,   233,   234,   235,    61,    62,   684,   428,   618,
     619,  1068,   642,   643,   587,    86,   656,   657,  1137,    92,
     833,    14,   342,   618,   619,   418,   860,   838,   839,   840,
     841,   842,   618,   619,   615,   845,   846,   847,   848,   855,
     856,   863,   864,   780,   781,   782,   561,   784,   785,   786,
    1081,  1082,  1137,   559,   582,   828,   829,   830,   676,    74,
    1133,    63,    64,    65,    66,    67,   293,    75,   477,    76,
     978,   979,   658,   659,   660,   661,   662,  1263,  1264,   307,
     805,   806,   686,   693,    68,   685,   673,   674,   620,   705,
     431,   644,    69,   686,    70,   663,   621,   835,   622,   645,
     616,   646,   620,   664,  1139,   665,   343,   614,  1130,  1131,
     621,   620,   803,   424,    31,    95,   919,   480,   679,   621,
     251,   899,   252,   625,   689,    41,   480,   330,   331,   680,
    1138,   525,   107,   108,   526,   109,   330,   331,  1139,   121,
     122,   993,   123,   330,   331,   302,   303,   330,   331,   980,
     330,   331,   480,   178,   485,   381,  1265,   981,   492,  1079,
      92,    51,   295,   296,  1266,   675,  1280,   330,   331,    32,
      33,    34,    35,    36,   432,   676,   330,   331,   916,    20,
      42,    43,    44,    45,    46,   330,   331,  1132,   330,   331,
     921,   527,    37,   528,   648,   330,   331,  1133,    15,   850,
      38,   481,    39,    47,   330,   331,   332,   330,   331,   858,
     482,    48,   333,    49,   334,   332,    52,    53,    54,    55,
      56,   457,   332,   334,   330,   331,   332,    26,   613,   332,
     334,  1076,   703,   509,   334,  1164,   483,   334,   486,    57,
     330,   331,   493,  1039,   330,   331,   332,    58,  1091,    59,
     480,   480,  1165,    16,   334,   332,   480,  1036,   330,   331,
      89,  1166,   485,   334,   332,   330,   331,   332,   330,   331,
    1167,    17,   334,  1173,   332,   334,   509,  1117,   978,   979,
    1178,    18,   334,   332,  1263,  1264,   332,   991,   992,  1213,
     578,   334,  1087,    19,   334,   610,   930,   480,   485,   610,
     727,   769,   937,   332,   480,   485,   742,   490,   490,  1214,
     495,   334,   495,   742,   495,   941,   966,   510,   956,   332,
     480,   480,  1020,   332,     1,  1215,   480,   334,   485,  1216,
    1001,   334,  1003,   956,   549,   550,  1027,   332,  1044,    90,
     551,   480,   480,  1217,   332,   334,   553,   332,    78,   480,
    1218,   485,   334,  1237,  1001,   334,  1003,   980,   626,   490,
     563,   495,  -219,  1265,   947,   981,   626,   495,  -218,  1189,
     742,  1266,  1189,   626,   579,   626,  1256,  1070,  1021,   611,
     258,   641,   655,   701,   728,   770,   938,   104,   779,   783,
     832,   851,   852,    94,   859,   118,   861,   918,   932,   942,
     172,    21,   957,    97,   997,   998,   944,   945,   946,  1289,
     999,  1290,  1000,    98,  1002,    99,  1004,  1013,   130,   131,
    1028,   100,  1045,    22,    23,  1055,  1056,   144,   145,   101,
    1187,  1241,  1008,  1057,  1174,  1058,   135,   136,  1059,   137,
    1060,   111,  1069,  1085,   132,  1088,  -219,   627,   628,   146,
    1114,  1122,  -218,  1190,  1221,   308,  1222,   915,   311,  1245,
    1257,   358,   359,   360,    22,    23,   149,   150,   361,   151,
     322,   296,  1210,  1211,  1005,  1006,  1007,   116,   117,   756,
     757,   112,   758,   368,   369,   370,   207,   208,   209,   210,
     211,    79,    80,    81,   214,   215,   216,   217,   219,   220,
     221,   222,   223,   113,     1,   114,   226,   227,   228,   229,
     364,   970,   115,   365,   156,   157,   158,   102,   103,   159,
     410,   411,   412,  1153,     2,     3,   125,   231,   710,   711,
     712,   371,   776,   713,   362,   363,   364,   372,   373,   365,
     126,   195,   196,   197,   198,   199,   788,   789,   790,   202,
     203,   204,   205,   127,     4,     5,     6,     7,   128,   873,
     874,   875,   876,   172,   353,  1191,   877,   356,   413,   357,
     161,   878,   879,     8,   414,   415,  1238,   183,   184,   185,
     186,   187,   888,   889,   890,   190,   191,   192,   193,   155,
     105,   106,   107,   108,   791,   109,   880,   397,   398,   399,
     792,   793,   129,   188,   119,   120,   121,   122,   139,   123,
     133,   134,   135,   136,   140,   137,  1267,   200,   141,   881,
    1269,  1270,   142,   212,   143,  1072,   571,  1282,  1283,   572,
     891,   390,   391,   734,   735,   736,   892,   893,   737,  1126,
    1127,  1128,  1129,   168,  1136,   162,  1142,   163,   147,   148,
     149,   150,   164,   151,   105,   106,   107,   108,   165,   109,
     166,   224,   169,   105,   106,   107,   108,   260,   109,   105,
     106,   107,   108,   167,   109,   170,   261,   175,   754,   755,
     756,   757,   262,   758,   105,   106,   107,   108,  1186,   109,
    1179,  1180,  1181,  1182,  1183,  1184,   171,   263,   105,   106,
     107,   108,   176,   109,   119,   120,   121,   122,   177,   123,
     178,   264,   181,   119,   120,   121,   122,   266,   123,   182,
     119,   120,   121,   122,   590,   123,   267,   572,   591,   392,
     393,   592,  1219,   268,   119,   120,   121,   122,   109,   123,
     119,   120,   121,   122,   194,   123,   189,   269,   123,   133,
     134,   135,   136,   270,   137,   133,   134,   135,   136,   137,
     137,   206,   272,   218,   133,   134,   135,   136,   273,   137,
     133,   134,   135,   136,   151,   137,   201,   274,   213,   133,
     134,   135,   136,   275,   137,   147,   148,   149,   150,   230,
     151,   595,   276,  1223,   572,  1225,   433,   434,   278,   147,
     148,   149,   150,   225,   151,   147,   148,   149,   150,   159,
     151,   232,   279,   236,   147,   148,   149,   150,   280,   151,
     147,   148,   149,   150,   237,   151,   238,   281,   239,   754,
     755,   756,   757,   282,   758,   754,   755,   756,   757,   240,
     758,  1247,   843,   241,   754,   755,   756,   757,   922,   758,
     443,   444,  1255,   754,   755,   756,   757,   923,   758,   754,
     755,   756,   757,   243,   758,   242,   924,   244,   754,   755,
     756,   757,   925,   758,   362,   363,   364,   597,   245,   365,
     592,   926,   249,   800,   711,   712,   248,   389,   713,   734,
     735,   736,   633,   250,   737,   572,   801,   265,   156,   157,
     158,   254,   826,   159,  1077,  1032,  1033,   681,   271,  1034,
     592,   862,   256,   156,   157,   158,   257,  1078,   159,  1278,
    1272,  1273,   725,   259,  1274,   726,  1209,   277,   105,   106,
     107,   108,  1279,   109,   286,   110,   119,   120,   121,   122,
     283,   123,   284,   124,   133,   134,   135,   136,   287,   137,
     285,   138,   147,   148,   149,   150,   288,   151,   289,   152,
     156,   157,   158,   712,   290,   159,   713,   160,   808,   711,
     712,   394,   395,   713,  1031,  1032,  1033,   914,   292,  1034,
     726,  1271,  1272,  1273,   736,  1175,  1274,   737,   429,   430,
     928,   931,   988,   592,   592,   592,  1042,  1046,  1119,   726,
     526,   726,  1033,  1125,  1157,  1034,   726,   726,  1248,  1273,
     297,   726,  1274,    82,    83,    84,   447,   448,   516,   517,
     516,   570,   516,   704,   767,   768,   777,   778,   298,   516,
     798,  1171,  1172,  1176,  1177,  1259,  1260,    28,    30,   291,
     300,   305,   301,   310,   312,   318,   313,   317,   319,   314,
     315,   316,   320,   323,   329,   336,   337,   338,   339,   340,
     344,   345,   346,   349,   347,   350,   351,   355,   352,   366,
     367,   374,   375,   376,   378,   379,   384,   380,   385,   383,
     386,   387,   365,   396,   400,   404,   403,   401,   405,   406,
     407,   408,   409,   419,   417,   420,   421,   422,   423,   424,
     437,   426,   441,   436,   451,   452,   453,   454,   455,   456,
     461,   472,   462,   458,   459,   460,   464,   466,   475,   468,
     478,   471,   465,   490,   495,   496,   473,   479,   484,   474,
     500,   505,   512,   487,   488,   514,   489,   519,   522,   532,
     491,   523,   494,   504,   533,   506,   534,   507,   508,   539,
     521,   513,   537,   541,   546,   556,   565,   566,   567,   577,
     581,   529,   524,   530,   535,   583,   588,   544,   594,   599,
     558,   531,   548,   552,   536,   542,   601,   554,   547,   555,
     564,   560,   602,   562,   603,   574,   605,   606,   580,   584,
     585,   575,   576,   586,   607,   631,   589,   593,   598,   600,
     632,   608,   604,   634,   639,   637,   636,   640,   700,   671,
     617,   670,   709,   682,   716,   690,   720,   723,   635,   733,
     724,   691,   730,   692,   742,   745,   753,   766,   796,   694,
     695,   696,   706,   697,   698,   807,   702,   809,   816,   812,
     817,   819,   836,   821,   717,   715,   719,   831,   718,   834,
     849,  1115,   853,   740,   721,   739,   865,   722,   896,   746,
     869,   897,   898,   743,   744,   901,   910,   747,   748,   749,
     902,   759,   750,   760,   764,   763,   772,   810,   774,   794,
     795,   713,   797,   799,   818,   911,   811,   820,   802,   917,
     815,   626,   927,   929,   825,   913,   737,   822,   936,   943,
     837,   758,   961,   827,   962,   969,   972,   973,   844,   866,
     854,   983,   857,   990,   867,  1014,   868,   870,   871,   872,
    1017,   975,  1018,   882,  1012,  1024,   511,   883,   884,  1043,
     885,   907,   294,  1152,   612,   971,   886,   887,   895,   994,
     382,   904,   905,   900,   995,  1065,   699,   958,   909,   908,
     933,  1083,   934,  1037,  1063,   935,   920,   912,   939,   940,
     950,   951,   952,   953,   954,   955,  1026,  1084,   965,   968,
    1047,   960,   959,  1086,   963,   964,   974,  1106,   967,  1048,
    1049,   976,  1050,  1052,  1054,   984,  1096,   977,  1098,  1107,
    1116,   985,   986,   987,   989,  1011,  1118,  1120,  1100,  1022,
    1149,  1161,  1123,  1019,  1101,  1015,  1102,  1103,  1016,  1025,
    1073,  1038,  1075,  1023,  1035,  1040,  1041,  1104,  1062,  1105,
    1124,  1162,  1170,  1192,  1194,  1051,  1053,  1195,  1061,  1064,
    1071,  1074,  1034,  1196,  1066,  1204,  1199,   624,  1092,  1093,
    1089,  1090,  1094,  1095,  1097,  1099,  1229,  1109,  1239,  1156,
    1240,  1261,  1243,  1111,  1112,  1158,  1110,  1143,  1144,  1121,
    1159,  1251,  1145,  1146,  1147,  1253,  1148,  1284,  1150,  1285,
    1151,  1154,  1287,  1292,  1294,  1168,  1155,  1224,  1293,  1226,
    1244,  1160,  1163,  1185,  1297,  1188,    96,  1193,  1197,  1198,
     996,  1200,  1201,  1202,  1203,   824,  1208,  1212,  1205,  1230,
    1246,  1228,  1250,  1227,  1242,  1231,   729,  1220,  1009,     0,
    1232,  1233,  1010,  1234,  1235,  1236,  1252,     0,  1249,     0,
       0,     0,     0,  1262,  1274,     0,     0,     0,  1258,     0,
    1291,     0,     0,     0,  1288,  1296,     0,     0,  1295,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,   502,
       0,   503
};

static const yytype_int16 yycheck[] =
{
      74,    75,   321,   376,   386,   569,   293,   516,   648,   405,
     406,   728,   493,   454,   680,   566,   682,   919,   585,   586,
     669,   670,   589,   470,   663,   664,   593,   675,   328,   685,
       4,   598,    32,   487,    88,   308,   355,   491,    92,  1019,
       8,  1132,     7,    52,   426,   644,   645,    15,     4,     3,
       4,     3,     4,    76,    27,   451,   452,   453,    23,    24,
       3,     4,     4,   544,    87,    83,    75,   521,    86,   620,
     621,   344,    87,   624,    39,     4,     4,    77,   980,   981,
    1171,  1172,   156,   157,   158,     3,     4,     4,   388,     3,
       4,  1071,     3,     4,   535,    69,     3,     4,     4,    72,
     740,    87,     4,     3,     4,   378,   772,   746,   747,   748,
     749,   750,     3,     4,   561,   754,   755,   756,   757,   767,
     768,   777,   778,   690,   691,   692,   508,   694,   695,   696,
    1032,  1033,     4,   506,   530,   734,   735,   736,    92,    82,
      92,    59,    60,    61,    62,    63,    88,    90,   435,    92,
       3,     4,    59,    60,    61,    62,    63,     3,     4,    88,
     711,   712,    90,   604,    82,    82,     3,     4,    82,   616,
       3,    82,    90,    90,    92,    82,    90,   741,    92,    90,
     562,    92,    82,    90,    90,    92,    88,   560,     3,     4,
      90,    82,    92,     6,     4,    27,     8,     4,    76,    90,
      28,    92,    30,    15,   600,     4,     4,     3,     4,    87,
      82,    88,    83,    84,    91,    86,     3,     4,    90,    83,
      84,   938,    86,     3,     4,    50,    51,     3,     4,    82,
       3,     4,     4,    52,     4,    54,    82,    90,     3,    92,
      72,     4,    89,    90,    90,    82,    92,     3,     4,    59,
      60,    61,    62,    63,    87,    92,     3,     4,   825,     0,
      59,    60,    61,    62,    63,     3,     4,    82,     3,     4,
     837,    29,    82,    31,    87,     3,     4,    92,    87,   760,
      90,    88,    92,    82,     3,     4,    82,     3,     4,   770,
      88,    90,    88,    92,    90,    82,    59,    60,    61,    62,
      63,    88,    82,    90,     3,     4,    82,    91,    88,    82,
      90,  1028,    88,     4,    90,    88,    88,    90,    88,    82,
       3,     4,    87,   989,     3,     4,    82,    90,  1045,    92,
       4,     4,    88,    87,    90,    82,     4,   986,     3,     4,
       4,    88,     4,    90,    82,     3,     4,    82,     3,     4,
      88,    87,    90,    88,    82,    90,     4,  1074,     3,     4,
      88,    87,    90,    82,     3,     4,    82,   934,   935,    88,
       3,    90,  1038,    87,    90,     4,   857,     4,     4,     4,
       3,     3,     3,    82,     4,     4,     4,     4,     4,    88,
       4,    90,     4,     4,     4,     3,   905,    88,     4,    82,
       4,     4,   966,    82,     5,    88,     4,    90,     4,    88,
       4,    90,     4,     4,    88,    88,     3,    82,     3,    88,
      88,     4,     4,    88,    82,    90,    88,    82,    87,     4,
      88,     4,    90,    88,     4,    90,     4,    82,     4,     4,
      88,     4,     4,    82,   885,    90,     4,     4,     4,     4,
       4,    90,     4,     4,    87,     4,     4,  1021,   967,    88,
     181,    88,    88,    88,    87,    87,    87,     3,    88,    88,
      88,    88,    88,    88,    88,     3,    88,    88,    88,    87,
      52,     4,    88,    90,    88,    88,   882,   883,   884,    91,
      88,    93,    88,    90,    88,    90,    88,    88,    57,    58,
      87,    90,    87,    67,    68,    88,    88,    68,    69,    90,
    1150,  1228,   953,    88,  1138,    88,    83,    84,    88,    86,
      88,    90,    88,    88,     3,    88,    88,    78,    79,     3,
      88,    88,    88,    88,    88,   256,    88,   824,   259,    88,
      88,     8,     9,    10,    67,    68,    83,    84,    15,    86,
      89,    90,  1176,  1177,   950,   951,   952,    47,    48,    83,
      84,    90,    86,    16,    17,    18,   125,   126,   127,   128,
     129,    36,    37,    38,   133,   134,   135,   136,   139,   140,
     141,   142,   143,    90,     5,    90,   147,   148,   149,   150,
      83,   910,    90,    86,    81,    82,    83,    37,    38,    86,
      16,    17,    18,  1112,    25,    26,    90,    94,    81,    82,
      83,    64,   686,    86,    81,    82,    83,    70,    71,    86,
      90,   111,   112,   113,   114,   115,    16,    17,    18,   119,
     120,   121,   122,    90,    55,    56,    57,    58,    90,    28,
      29,    30,    31,    52,    53,  1154,    35,   332,    64,   334,
      87,    40,    41,    74,    70,    71,  1220,    97,    98,    99,
     100,   101,    16,    17,    18,   105,   106,   107,   108,     3,
      81,    82,    83,    84,    64,    86,    65,   362,   363,   364,
      70,    71,    90,    94,    81,    82,    83,    84,    90,    86,
      81,    82,    83,    84,    90,    86,  1261,    94,    90,    88,
    1265,  1266,    90,    94,    90,  1024,    88,  1272,  1273,    91,
      64,     3,     4,    81,    82,    83,    70,    71,    86,  1092,
    1093,  1094,  1095,    87,  1097,     4,  1099,     4,    81,    82,
      83,    84,     3,    86,    81,    82,    83,    84,     4,    86,
       4,    94,    87,    81,    82,    83,    84,    94,    86,    81,
      82,    83,    84,     3,    86,     3,    94,    87,    81,    82,
      83,    84,    94,    86,    81,    82,    83,    84,  1150,    86,
    1143,  1144,  1145,  1146,  1147,  1148,     3,    94,    81,    82,
      83,    84,    87,    86,    81,    82,    83,    84,    27,    86,
      52,    94,    87,    81,    82,    83,    84,    94,    86,    27,
      81,    82,    83,    84,    88,    86,    94,    91,    88,     3,
       4,    91,  1185,    94,    81,    82,    83,    84,    86,    86,
      81,    82,    83,    84,     3,    86,    91,    94,    86,    81,
      82,    83,    84,    94,    86,    81,    82,    83,    84,    86,
      86,     3,    94,     3,    81,    82,    83,    84,    94,    86,
      81,    82,    83,    84,    86,    86,    91,    94,    91,    81,
      82,    83,    84,    94,    86,    81,    82,    83,    84,     3,
      86,    88,    94,  1192,    91,  1194,    40,    41,    94,    81,
      82,    83,    84,    91,    86,    81,    82,    83,    84,    86,
      86,    91,    94,     3,    81,    82,    83,    84,    94,    86,
      81,    82,    83,    84,    32,    86,    91,    94,    91,    81,
      82,    83,    84,    94,    86,    81,    82,    83,    84,     4,
      86,  1240,    94,    91,    81,    82,    83,    84,    94,    86,
      75,    76,  1251,    81,    82,    83,    84,    94,    86,    81,
      82,    83,    84,     4,    86,    91,    94,    87,    81,    82,
      83,    84,    94,    86,    81,    82,    83,    88,     4,    86,
      91,    94,    32,    81,    82,    83,    65,    94,    86,    81,
      82,    83,    88,    87,    86,    91,    94,     3,    81,    82,
      83,     4,    94,    86,    81,    82,    83,    88,     3,    86,
      91,    94,    87,    81,    82,    83,    87,    94,    86,    81,
      82,    83,    88,    87,    86,    91,    94,     3,    81,    82,
      83,    84,    94,    86,     4,    88,    81,    82,    83,    84,
       3,    86,     3,    88,    81,    82,    83,    84,     4,    86,
       3,    88,    81,    82,    83,    84,    91,    86,     4,    88,
      81,    82,    83,    83,     4,    86,    86,    88,    81,    82,
      83,     3,     4,    86,    81,    82,    83,    88,    32,    86,
      91,    81,    82,    83,    83,  1139,    86,    86,     3,     4,
      88,    88,    88,    91,    91,    91,    88,    88,    88,    91,
      91,    91,    83,    88,    88,    86,    91,    91,    88,    83,
       3,    91,    86,    36,    37,    38,    75,    76,    87,    88,
      87,    88,    87,    88,    81,    82,    81,    82,     3,    87,
      88,    81,    82,    81,    82,    20,    21,    13,    14,    91,
       3,     8,    87,    49,    93,     4,    93,    88,     4,    93,
      93,    93,     3,     3,    65,    42,    33,    88,     3,     8,
       3,    49,    87,    91,    88,    23,     4,     3,    23,     3,
       3,     3,    88,    87,     3,    65,     4,    87,     4,    92,
      87,    53,    86,    92,     3,    87,    91,    35,    87,    87,
      87,    87,    87,     3,    88,    65,    87,    54,     3,     6,
       3,    87,     3,    34,    87,    87,    87,    87,    87,    87,
       3,    75,     4,    43,    88,    88,    87,     4,     4,    87,
       3,    87,    91,     4,     4,     3,    91,    88,    88,    91,
       3,    43,     3,    87,    87,     4,    88,     4,     3,    14,
      87,     4,    88,    87,    14,    87,    14,    88,    87,     4,
      87,    91,    14,    14,    14,     4,     4,     8,     4,     4,
      42,    88,    97,    87,    87,     8,     8,    87,     8,     8,
      87,    96,    88,    88,    96,    96,    14,    88,    96,    88,
      93,    87,    14,    87,    14,    93,    14,    14,    87,    87,
      87,    93,    92,    87,    14,    14,    87,    87,    87,    87,
       4,    27,    87,     3,    33,     4,    65,     3,    44,     4,
      94,    87,     3,    87,    15,    87,    14,     3,    97,     3,
      97,    87,    14,    87,     4,    14,     3,     3,    44,    87,
      87,    87,    82,    87,    87,     3,    88,     3,     3,     6,
       3,     3,    15,     4,    88,    92,    87,     3,   630,     4,
       3,  1071,     4,    87,    91,    88,    14,    92,     4,    90,
      14,     3,     3,    88,    88,     3,     3,    90,    90,    90,
       4,    88,    90,    87,    83,    88,    87,    92,    88,    87,
      87,    86,    88,    95,    66,     3,    88,    65,    91,     3,
      87,     4,     3,     3,    87,    34,    86,    91,     3,     3,
      87,    86,     3,    91,     3,     3,     3,     3,    91,    88,
      91,     3,    87,     4,    88,     3,    88,    88,    88,    88,
       3,    29,     4,    87,    14,     3,   464,    87,    87,     3,
      87,   815,   246,  1109,   558,    66,    87,    87,    87,    33,
     348,    88,    87,    91,    33,     3,   610,   895,    91,    93,
      83,     3,    87,    83,    14,    87,    92,    97,    87,    87,
      87,    87,    87,    87,    87,    87,    34,     3,    80,    88,
      45,    91,    93,     4,    91,    91,    91,     4,    87,    45,
      45,    88,    45,    45,    45,    88,     8,    93,     8,     4,
       3,    93,    87,    93,    87,    82,     3,     3,    45,    80,
      46,     3,    34,    87,    45,    91,    45,    45,    93,    88,
      65,    87,    65,    93,    91,    88,    88,    45,    87,    45,
      34,     3,     3,     3,     3,    96,    96,     3,    95,    93,
      87,    87,    86,     3,    93,     4,    34,     8,    87,    87,
      91,    91,    87,    87,    87,    87,     3,    87,     3,    66,
       3,    11,     4,    88,    87,    66,    93,    87,    87,    93,
      65,     3,    87,    87,    87,     4,    87,     3,    87,     4,
      88,    87,     3,     3,     3,    83,    88,    65,     4,    66,
      47,    91,    91,    87,     3,    88,    30,    88,    88,    88,
     942,    88,    88,    88,    88,   729,    88,    88,    91,    83,
      66,    87,    87,    93,    93,    88,   640,  1186,   954,    -1,
      88,    88,   955,    88,    88,    88,    88,    -1,    83,    -1,
      -1,    -1,    -1,    87,    86,    -1,    -1,    -1,    96,    -1,
      91,    -1,    -1,    -1,    97,    93,    -1,    -1,    97,    -1,
      -1,    -1,    -1,    -1,    -1,    -1,    -1,    -1,    -1,    -1,
      -1,    -1,    -1,    -1,    -1,    -1,    -1,    -1,    -1,   455,
      -1,   456
};

  /* YYSTOS[STATE-NUM] -- The (internal number of the) accessing
     symbol of state STATE-NUM.  */
static const yytype_uint8 yystos[] =
{
       0,     5,    25,    26,    55,    56,    57,    58,    74,    99,
     129,     4,   130,    87,    87,    87,    87,    87,    87,    87,
       0,     4,    67,    68,   109,   140,    91,   118,   129,   119,
     129,     4,    59,    60,    61,    62,    63,    82,    90,    92,
     164,     4,    59,    60,    61,    62,    63,    82,    90,    92,
     165,     4,    59,    60,    61,    62,    63,    82,    90,    92,
     166,     3,     4,    59,    60,    61,    62,    63,    82,    90,
      92,   168,     3,     4,    82,    90,    92,   177,    87,    36,
      37,    38,    36,    37,    38,     4,    69,    32,    77,     4,
      88,    27,    72,   131,    88,    27,   131,    90,    90,    90,
      90,    90,   164,   164,     3,    81,    82,    83,    84,    86,
      88,    90,    90,    90,    90,    90,   165,   165,     3,    81,
      82,    83,    84,    86,    88,    90,    90,    90,    90,    90,
     166,   166,     3,    81,    82,    83,    84,    86,    88,    90,
      90,    90,    90,    90,   168,   168,     3,    81,    82,    83,
      84,    86,    88,   177,   177,     3,    81,    82,    83,    86,
      88,    87,     4,     4,     3,     4,     4,     3,    87,    87,
       3,     3,    52,   101,   114,    87,    87,    27,    52,   102,
     115,    87,    27,   164,   164,   164,   164,   164,    94,    91,
     164,   164,   164,   164,     3,   165,   165,   165,   165,   165,
      94,    91,   165,   165,   165,   165,     3,   166,   166,   166,
     166,   166,    94,    91,   166,   166,   166,   166,     3,   168,
     168,   168,   168,   168,    94,    91,   168,   168,   168,   168,
       3,    94,    91,   177,   177,   177,     3,    32,    91,    91,
       4,    91,    91,     4,    87,     4,   111,   112,    65,    32,
      87,    28,    30,   135,     4,   132,    87,    87,   135,    87,
      94,    94,    94,    94,    94,     3,    94,    94,    94,    94,
      94,     3,    94,    94,    94,    94,    94,     3,    94,    94,
      94,    94,    94,     3,     3,     3,     4,     4,    91,     4,
       4,    91,    32,    88,   112,    89,    90,     3,     3,   117,
       3,    87,    50,    51,   113,     8,     4,    88,   135,   116,
      49,   135,    93,    93,    93,    93,    93,    88,     4,     4,
       3,   140,    89,     3,     7,    23,    24,    39,   100,    65,
       3,     4,    82,    88,    90,   160,    42,    33,    88,     3,
       8,   113,     4,    88,     3,    49,    87,    88,   100,    91,
      23,     4,    23,    53,   114,     3,   160,   160,     8,     9,
      10,    15,    81,    82,    83,    86,     3,     3,    16,    17,
      18,    64,    70,    71,     3,    88,    87,   113,     3,    65,
      87,    54,   115,    92,     4,     4,    87,    53,   100,    94,
       3,     4,     3,     4,     3,     4,    92,   160,   160,   160,
       3,    35,   136,    91,    87,    87,    87,    87,    87,    87,
      16,    17,    18,    64,    70,    71,   117,    88,   113,     3,
      65,    87,    54,     3,     6,   143,    87,    75,   114,     3,
       4,     3,    87,    40,    41,   139,    34,     3,   150,   150,
     150,     3,   151,    75,    76,   152,   153,    75,    76,   155,
     156,    87,    87,    87,    87,    87,    87,    88,    43,    88,
      88,     3,     4,   110,    87,    91,     4,   144,    87,   106,
     143,    87,    75,    91,    91,     4,   137,   140,     3,    88,
       4,    88,    88,    88,    88,     4,    88,    87,    87,    88,
       4,    87,     3,    87,    88,     4,     3,   150,   150,   150,
       3,   151,   152,   155,    87,    43,    87,    88,    87,     4,
      88,   110,     3,    91,     4,   162,    87,    88,   106,     4,
     133,    87,     3,     4,    97,    88,    91,    29,    31,    88,
      87,    96,    14,    14,    14,    87,    96,    14,   133,     4,
     134,    14,    96,   133,    87,   134,    14,    96,    88,    88,
      88,    88,    88,    88,    88,    88,     4,   121,    87,   117,
      87,   143,    87,    88,    93,     4,     8,     4,   148,   162,
      88,    88,    91,   133,    93,    93,    92,     4,     3,    87,
      87,    42,   150,     8,    87,    87,    87,   151,     8,    87,
      88,    88,    91,    87,     8,    88,   134,    88,    87,     8,
      87,    14,    14,    14,    87,    14,    14,    14,    27,   122,
       4,    88,   121,    88,   117,   106,   143,    94,     3,     4,
      82,    90,    92,   163,     8,    15,     4,    78,    79,   103,
     148,    14,     4,    88,     3,    97,    65,     4,   138,    33,
       3,    88,     3,     4,    82,    90,    92,   159,    87,   141,
     142,   143,   149,   141,   141,    88,     3,     4,    59,    60,
      61,    62,    63,    82,    90,    92,   167,   141,    76,    87,
      87,     4,   141,     3,     4,    82,    92,   169,   170,    76,
      87,    88,    87,   141,     4,    82,    90,   173,   174,   150,
      87,    87,    87,   151,    87,    87,    87,    87,    87,   122,
      44,    88,    88,    88,    88,   106,    82,   163,   163,     3,
      81,    82,    83,    86,   163,    92,    15,    88,   103,    87,
      14,    91,    92,     3,    97,    88,    91,     3,    87,   136,
      14,   159,   159,     3,    81,    82,    83,    86,   149,    88,
      87,   147,     4,    88,    88,    14,    90,    90,    90,    90,
      90,   167,   167,     3,    81,    82,    83,    84,    86,    88,
      87,   153,   153,    88,    83,   170,     3,    81,    82,     3,
      87,   156,    87,   156,    88,   174,   177,    81,    82,    88,
     141,   141,   141,    88,   141,   141,   141,   123,    16,    17,
      18,    64,    70,    71,    87,    87,    44,    88,    88,    95,
      81,    94,    91,    92,   163,   163,   163,     3,    81,     3,
      92,    88,     6,   104,   145,    87,     3,     3,    66,     3,
      65,     4,    91,   138,   139,    87,    94,    91,   159,   159,
     159,     3,    88,   149,     4,   148,    15,    87,   167,   167,
     167,   167,   167,    94,    91,   167,   167,   167,   167,     3,
     134,    88,    88,     4,    91,   170,   170,    87,   134,    88,
     156,    88,    94,   174,   174,    14,    88,    88,    88,    14,
      88,    88,    88,    28,    29,    30,    31,    35,    40,    41,
      65,    88,    87,    87,    87,    87,    87,    87,    16,    17,
      18,    64,    70,    71,   124,    87,     4,     3,     3,    92,
      91,     3,     4,   146,    88,    87,   107,   104,    93,    91,
       3,     3,    97,    34,    88,   140,   141,     3,    88,     8,
      92,   141,    94,    94,    94,    94,    94,     3,    88,     3,
     134,    88,    88,    83,    87,    87,     3,     3,    87,    87,
      87,     3,    87,     3,   150,   150,   150,   151,   154,   157,
      87,    87,    87,    87,    87,    87,     4,    88,   124,    93,
      91,     3,     3,    91,    91,    80,   162,    87,    88,     3,
     100,    66,     3,     3,    91,    29,    88,    93,     3,     4,
      82,    90,   158,     3,    88,    93,    87,    93,    88,    87,
       4,   141,   141,   138,    33,    33,   137,    88,    88,    88,
      88,     4,    88,     4,    88,   150,   150,   150,   151,   154,
     157,    82,    14,    88,     3,    91,    93,     3,     4,    87,
     148,   162,    80,    93,     3,    88,    34,     3,    87,   158,
     158,    81,    82,    83,    86,    91,   153,    83,    87,   156,
      88,    88,    88,     3,     3,    87,    88,    45,    45,    45,
      45,    96,    45,    96,    45,    88,    88,    88,    88,    88,
      88,    95,    87,    14,    93,     3,    93,   105,   145,    88,
     148,    87,   100,    65,    87,    65,   138,    81,    94,    92,
     158,   158,   158,     3,     3,    88,     4,   156,    88,    91,
      91,   138,    87,    87,    87,    87,     8,    87,     8,    87,
      45,    45,    45,    45,    45,    45,     4,     4,   120,    87,
      93,    88,    87,   108,    88,   105,     3,   138,     3,    88,
       3,    93,    88,    34,    34,    88,   117,   117,   117,   117,
       3,     4,    82,    92,   171,   172,   117,     4,    82,    90,
     175,   176,   117,    87,    87,    87,    87,    87,    87,    46,
      87,    88,   120,   162,    87,    88,    66,    88,    66,    65,
      91,     3,     3,    91,    88,    88,    88,    88,    83,   172,
       3,    81,    82,    88,   176,   177,    81,    82,    88,   117,
     117,   117,   117,   117,   117,    87,   143,   149,    88,     4,
      88,   162,     3,    88,     3,     3,     3,    88,    88,    34,
      88,    88,    88,    88,     4,    91,   172,   172,    88,    94,
     176,   176,    88,    88,    88,    88,    88,    88,    88,   117,
     147,    88,    88,   100,    65,   100,    66,    93,    87,     3,
      83,    88,    88,    88,    88,    88,    88,    88,   148,     3,
       3,   138,    93,     4,    47,    88,    66,   100,    88,    83,
      87,     3,    88,     4,   125,   100,     4,    88,    96,    20,
      21,    11,    87,     3,     4,    82,    90,   161,   126,   161,
     161,    81,    82,    83,    86,    88,    92,   127,    81,    94,
      92,   161,   161,   161,     3,     4,   128,     3,    97,    91,
      93,    91,     3,     4,     3,    97,    93,     3
};

  /* YYR1[YYN] -- Symbol number of symbol that rule YYN derives.  */
static const yytype_uint8 yyr1[] =
{
       0,    98,    99,    99,    99,    99,    99,    99,    99,    99,
      99,    99,    99,    99,    99,    99,    99,   100,   100,   100,
     100,   101,   102,   103,   103,   103,   104,   105,   106,   106,
     107,   107,   108,   108,   109,   109,   110,   110,   111,   111,
     112,   112,   113,   113,   114,   115,   116,   116,   117,   117,
     117,   117,   117,   117,   117,   117,   117,   118,   118,   118,
     118,   118,   118,   118,   118,   118,   118,   118,   118,   118,
     118,   118,   118,   119,   119,   120,   120,   121,   121,   121,
     121,   121,   121,   121,   121,   121,   121,   121,   121,   122,
     122,   123,   123,   123,   123,   123,   123,   123,   123,   123,
     123,   123,   123,   124,   124,   124,   125,   125,   125,   126,
     126,   127,   128,   128,   129,   130,   130,   131,   132,   132,
     133,   133,   133,   134,   134,   134,   135,   135,   135,   135,
     135,   135,   136,   136,   137,   137,   138,   138,   139,   139,
     140,   140,   140,   140,   140,   140,   141,   141,   141,   142,
     142,   143,   144,   144,   145,   146,   146,   147,   147,   148,
     148,   149,   149,   150,   150,   151,   151,   152,   152,   152,
     152,   153,   153,   154,   154,   155,   155,   155,   155,   155,
     155,   156,   156,   157,   157,   158,   158,   158,   158,   158,
     158,   158,   158,   159,   159,   159,   159,   159,   159,   159,
     159,   159,   160,   160,   160,   160,   160,   160,   160,   160,
     161,   161,   161,   161,   161,   161,   161,   161,   162,   162,
     163,   163,   163,   163,   163,   163,   163,   163,   163,   164,
     164,   164,   164,   164,   164,   164,   164,   164,   164,   164,
     164,   164,   164,   165,   165,   165,   165,   165,   165,   165,
     165,   165,   165,   165,   165,   165,   165,   166,   166,   166,
     166,   166,   166,   166,   166,   166,   166,   166,   166,   166,
     166,   167,   167,   167,   167,   167,   167,   167,   167,   167,
     167,   167,   167,   167,   167,   167,   168,   168,   168,   168,
     168,   168,   168,   168,   168,   168,   168,   168,   168,   168,
     168,   169,   169,   169,   169,   170,   170,   170,   170,   170,
     171,   171,   171,   171,   172,   172,   172,   172,   172,   173,
     173,   173,   173,   174,   174,   174,   175,   175,   175,   175,
     176,   176,   176,   177,   177,   177,   177,   177,   177,   177,
     177,   177
};

  /* YYR2[YYN] -- Number of symbols on the right hand side of rule YYN.  */
static const yytype_uint8 yyr2[] =
{
       0,     2,     4,     5,     4,     5,    13,    12,    21,    22,
      13,    12,     4,     4,     4,     4,     4,     2,     3,     3,
       1,     1,     1,     1,     1,     0,     2,     2,     6,     5,
       5,     4,     4,     3,    15,    14,     6,     5,     3,     2,
      13,     1,     1,     1,     4,     4,     5,     0,     4,     4,
       4,     8,     4,     4,     4,     8,     0,    14,    14,    14,
      14,    14,    14,    17,    17,    15,    15,    15,    15,    15,
      15,    18,    18,    20,    21,     4,     6,    13,    12,    13,
      12,    13,    12,    13,    12,    13,    12,    13,    12,     4,
       0,     3,     3,     5,     2,     2,     3,     3,     9,     9,
       5,    13,     0,    17,    14,     0,    11,     5,     0,     2,
       0,     3,     5,     3,     2,     3,     1,     4,     4,     3,
       3,     1,     0,     3,     1,     0,    14,    20,    16,    24,
      20,    22,     2,     4,     9,     7,     5,     3,     1,     1,
       5,     5,     6,     5,     5,     6,     3,     1,     1,     4,
       3,     2,     3,     1,     2,     3,     1,    10,     0,     8,
       7,     8,     0,     5,     0,     5,     0,    11,     7,     7,
       1,     5,     0,     5,     0,    11,    12,     7,     7,     8,
       1,     5,     0,     5,     0,     3,     3,     3,     3,     3,
       2,     1,     1,     3,     3,     3,     3,     3,     2,     1,
       5,     1,     3,     3,     3,     3,     3,     2,     1,     1,
       3,     3,     3,     3,     3,     2,     1,     1,    10,     9,
       3,     3,     3,     3,     3,     2,     1,     5,     1,     3,
       3,     3,     3,     3,     4,     4,     4,     4,     4,     3,
       2,     1,     5,     3,     3,     3,     3,     3,     4,     4,
       4,     4,     4,     3,     2,     1,     5,     3,     3,     3,
       3,     3,     4,     4,     4,     4,     4,     3,     2,     1,
       5,     3,     3,     3,     3,     3,     4,     4,     4,     4,
       4,     3,     2,     1,     5,     1,     3,     3,     3,     3,
       3,     4,     4,     4,     4,     4,     3,     2,     1,     5,
       1,     3,     3,     2,     1,     3,     7,     1,     5,     1,
       3,     3,     2,     1,     3,     7,     1,     5,     1,     3,
       3,     2,     1,     5,     1,     3,     3,     3,     2,     1,
       5,     1,     3,     3,     3,     3,     3,     3,     2,     1,
       5,     1
};


#define yyerrok         (yyerrstatus = 0)
#define yyclearin       (yychar = YYEMPTY)
#define YYEMPTY         (-2)
#define YYEOF           0

#define YYACCEPT        goto yyacceptlab
#define YYABORT         goto yyabortlab
#define YYERROR         goto yyerrorlab


#define YYRECOVERING()  (!!yyerrstatus)

#define YYBACKUP(Token, Value)                                  \
do                                                              \
  if (yychar == YYEMPTY)                                        \
    {                                                           \
      yychar = (Token);                                         \
      yylval = (Value);                                         \
      YYPOPSTACK (yylen);                                       \
      yystate = *yyssp;                                         \
      goto yybackup;                                            \
    }                                                           \
  else                                                          \
    {                                                           \
      yyerror (YY_("syntax error: cannot back up")); \
      YYERROR;                                                  \
    }                                                           \
while (0)

/* Error token number */
#define YYTERROR        1
#define YYERRCODE       256



/* Enable debugging if requested.  */
#if YYDEBUG

# ifndef YYFPRINTF
#  include <stdio.h> /* INFRINGES ON USER NAME SPACE */
#  define YYFPRINTF fprintf
# endif

# define YYDPRINTF(Args)                        \
do {                                            \
  if (yydebug)                                  \
    YYFPRINTF Args;                             \
} while (0)

/* This macro is provided for backward compatibility. */
#ifndef YY_LOCATION_PRINT
# define YY_LOCATION_PRINT(File, Loc) ((void) 0)
#endif


# define YY_SYMBOL_PRINT(Title, Type, Value, Location)                    \
do {                                                                      \
  if (yydebug)                                                            \
    {                                                                     \
      YYFPRINTF (stderr, "%s ", Title);                                   \
      yy_symbol_print (stderr,                                            \
                  Type, Value); \
      YYFPRINTF (stderr, "\n");                                           \
    }                                                                     \
} while (0)


/*----------------------------------------.
| Print this symbol's value on YYOUTPUT.  |
`----------------------------------------*/

static void
yy_symbol_value_print (FILE *yyoutput, int yytype, YYSTYPE const * const yyvaluep)
{
  FILE *yyo = yyoutput;
  YYUSE (yyo);
  if (!yyvaluep)
    return;
# ifdef YYPRINT
  if (yytype < YYNTOKENS)
    YYPRINT (yyoutput, yytoknum[yytype], *yyvaluep);
# endif
  YYUSE (yytype);
}


/*--------------------------------.
| Print this symbol on YYOUTPUT.  |
`--------------------------------*/

static void
yy_symbol_print (FILE *yyoutput, int yytype, YYSTYPE const * const yyvaluep)
{
  YYFPRINTF (yyoutput, "%s %s (",
             yytype < YYNTOKENS ? "token" : "nterm", yytname[yytype]);

  yy_symbol_value_print (yyoutput, yytype, yyvaluep);
  YYFPRINTF (yyoutput, ")");
}

/*------------------------------------------------------------------.
| yy_stack_print -- Print the state stack from its BOTTOM up to its |
| TOP (included).                                                   |
`------------------------------------------------------------------*/

static void
yy_stack_print (yytype_int16 *yybottom, yytype_int16 *yytop)
{
  YYFPRINTF (stderr, "Stack now");
  for (; yybottom <= yytop; yybottom++)
    {
      int yybot = *yybottom;
      YYFPRINTF (stderr, " %d", yybot);
    }
  YYFPRINTF (stderr, "\n");
}

# define YY_STACK_PRINT(Bottom, Top)                            \
do {                                                            \
  if (yydebug)                                                  \
    yy_stack_print ((Bottom), (Top));                           \
} while (0)


/*------------------------------------------------.
| Report that the YYRULE is going to be reduced.  |
`------------------------------------------------*/

static void
yy_reduce_print (yytype_int16 *yyssp, YYSTYPE *yyvsp, int yyrule)
{
  unsigned long int yylno = yyrline[yyrule];
  int yynrhs = yyr2[yyrule];
  int yyi;
  YYFPRINTF (stderr, "Reducing stack by rule %d (line %lu):\n",
             yyrule - 1, yylno);
  /* The symbols being reduced.  */
  for (yyi = 0; yyi < yynrhs; yyi++)
    {
      YYFPRINTF (stderr, "   $%d = ", yyi + 1);
      yy_symbol_print (stderr,
                       yystos[yyssp[yyi + 1 - yynrhs]],
                       &(yyvsp[(yyi + 1) - (yynrhs)])
                                              );
      YYFPRINTF (stderr, "\n");
    }
}

# define YY_REDUCE_PRINT(Rule)          \
do {                                    \
  if (yydebug)                          \
    yy_reduce_print (yyssp, yyvsp, Rule); \
} while (0)

/* Nonzero means print parse trace.  It is left uninitialized so that
   multiple parsers can coexist.  */
int yydebug;
#else /* !YYDEBUG */
# define YYDPRINTF(Args)
# define YY_SYMBOL_PRINT(Title, Type, Value, Location)
# define YY_STACK_PRINT(Bottom, Top)
# define YY_REDUCE_PRINT(Rule)
#endif /* !YYDEBUG */


/* YYINITDEPTH -- initial size of the parser's stacks.  */
#ifndef YYINITDEPTH
# define YYINITDEPTH 200
#endif

/* YYMAXDEPTH -- maximum size the stacks can grow to (effective only
   if the built-in stack extension method is used).

   Do not make this value too large; the results are undefined if
   YYSTACK_ALLOC_MAXIMUM < YYSTACK_BYTES (YYMAXDEPTH)
   evaluated with infinite-precision integer arithmetic.  */

#ifndef YYMAXDEPTH
# define YYMAXDEPTH 10000
#endif


#if YYERROR_VERBOSE

# ifndef yystrlen
#  if defined __GLIBC__ && defined _STRING_H
#   define yystrlen strlen
#  else
/* Return the length of YYSTR.  */
static YYSIZE_T
yystrlen (const char *yystr)
{
  YYSIZE_T yylen;
  for (yylen = 0; yystr[yylen]; yylen++)
    continue;
  return yylen;
}
#  endif
# endif

# ifndef yystpcpy
#  if defined __GLIBC__ && defined _STRING_H && defined _GNU_SOURCE
#   define yystpcpy stpcpy
#  else
/* Copy YYSRC to YYDEST, returning the address of the terminating '\0' in
   YYDEST.  */
static char *
yystpcpy (char *yydest, const char *yysrc)
{
  char *yyd = yydest;
  const char *yys = yysrc;

  while ((*yyd++ = *yys++) != '\0')
    continue;

  return yyd - 1;
}
#  endif
# endif

# ifndef yytnamerr
/* Copy to YYRES the contents of YYSTR after stripping away unnecessary
   quotes and backslashes, so that it's suitable for yyerror.  The
   heuristic is that double-quoting is unnecessary unless the string
   contains an apostrophe, a comma, or backslash (other than
   backslash-backslash).  YYSTR is taken from yytname.  If YYRES is
   null, do not copy; instead, return the length of what the result
   would have been.  */
static YYSIZE_T
yytnamerr (char *yyres, const char *yystr)
{
  if (*yystr == '"')
    {
      YYSIZE_T yyn = 0;
      char const *yyp = yystr;

      for (;;)
        switch (*++yyp)
          {
          case '\'':
          case ',':
            goto do_not_strip_quotes;

          case '\\':
            if (*++yyp != '\\')
              goto do_not_strip_quotes;
            /* Fall through.  */
          default:
            if (yyres)
              yyres[yyn] = *yyp;
            yyn++;
            break;

          case '"':
            if (yyres)
              yyres[yyn] = '\0';
            return yyn;
          }
    do_not_strip_quotes: ;
    }

  if (! yyres)
    return yystrlen (yystr);

  return yystpcpy (yyres, yystr) - yyres;
}
# endif

/* Copy into *YYMSG, which is of size *YYMSG_ALLOC, an error message
   about the unexpected token YYTOKEN for the state stack whose top is
   YYSSP.

   Return 0 if *YYMSG was successfully written.  Return 1 if *YYMSG is
   not large enough to hold the message.  In that case, also set
   *YYMSG_ALLOC to the required number of bytes.  Return 2 if the
   required number of bytes is too large to store.  */
static int
yysyntax_error (YYSIZE_T *yymsg_alloc, char **yymsg,
                yytype_int16 *yyssp, int yytoken)
{
  YYSIZE_T yysize0 = yytnamerr (YY_NULLPTR, yytname[yytoken]);
  YYSIZE_T yysize = yysize0;
  enum { YYERROR_VERBOSE_ARGS_MAXIMUM = 5 };
  /* Internationalized format string. */
  const char *yyformat = YY_NULLPTR;
  /* Arguments of yyformat. */
  char const *yyarg[YYERROR_VERBOSE_ARGS_MAXIMUM];
  /* Number of reported tokens (one for the "unexpected", one per
     "expected"). */
  int yycount = 0;

  /* There are many possibilities here to consider:
     - If this state is a consistent state with a default action, then
       the only way this function was invoked is if the default action
       is an error action.  In that case, don't check for expected
       tokens because there are none.
     - The only way there can be no lookahead present (in yychar) is if
       this state is a consistent state with a default action.  Thus,
       detecting the absence of a lookahead is sufficient to determine
       that there is no unexpected or expected token to report.  In that
       case, just report a simple "syntax error".
     - Don't assume there isn't a lookahead just because this state is a
       consistent state with a default action.  There might have been a
       previous inconsistent state, consistent state with a non-default
       action, or user semantic action that manipulated yychar.
     - Of course, the expected token list depends on states to have
       correct lookahead information, and it depends on the parser not
       to perform extra reductions after fetching a lookahead from the
       scanner and before detecting a syntax error.  Thus, state merging
       (from LALR or IELR) and default reductions corrupt the expected
       token list.  However, the list is correct for canonical LR with
       one exception: it will still contain any token that will not be
       accepted due to an error action in a later state.
  */
  if (yytoken != YYEMPTY)
    {
      int yyn = yypact[*yyssp];
      yyarg[yycount++] = yytname[yytoken];
      if (!yypact_value_is_default (yyn))
        {
          /* Start YYX at -YYN if negative to avoid negative indexes in
             YYCHECK.  In other words, skip the first -YYN actions for
             this state because they are default actions.  */
          int yyxbegin = yyn < 0 ? -yyn : 0;
          /* Stay within bounds of both yycheck and yytname.  */
          int yychecklim = YYLAST - yyn + 1;
          int yyxend = yychecklim < YYNTOKENS ? yychecklim : YYNTOKENS;
          int yyx;

          for (yyx = yyxbegin; yyx < yyxend; ++yyx)
            if (yycheck[yyx + yyn] == yyx && yyx != YYTERROR
                && !yytable_value_is_error (yytable[yyx + yyn]))
              {
                if (yycount == YYERROR_VERBOSE_ARGS_MAXIMUM)
                  {
                    yycount = 1;
                    yysize = yysize0;
                    break;
                  }
                yyarg[yycount++] = yytname[yyx];
                {
                  YYSIZE_T yysize1 = yysize + yytnamerr (YY_NULLPTR, yytname[yyx]);
                  if (! (yysize <= yysize1
                         && yysize1 <= YYSTACK_ALLOC_MAXIMUM))
                    return 2;
                  yysize = yysize1;
                }
              }
        }
    }

  switch (yycount)
    {
# define YYCASE_(N, S)                      \
      case N:                               \
        yyformat = S;                       \
      break
    default: /* Avoid compiler warnings. */
      YYCASE_(0, YY_("syntax error"));
      YYCASE_(1, YY_("syntax error, unexpected %s"));
      YYCASE_(2, YY_("syntax error, unexpected %s, expecting %s"));
      YYCASE_(3, YY_("syntax error, unexpected %s, expecting %s or %s"));
      YYCASE_(4, YY_("syntax error, unexpected %s, expecting %s or %s or %s"));
      YYCASE_(5, YY_("syntax error, unexpected %s, expecting %s or %s or %s or %s"));
# undef YYCASE_
    }

  {
    YYSIZE_T yysize1 = yysize + yystrlen (yyformat);
    if (! (yysize <= yysize1 && yysize1 <= YYSTACK_ALLOC_MAXIMUM))
      return 2;
    yysize = yysize1;
  }

  if (*yymsg_alloc < yysize)
    {
      *yymsg_alloc = 2 * yysize;
      if (! (yysize <= *yymsg_alloc
             && *yymsg_alloc <= YYSTACK_ALLOC_MAXIMUM))
        *yymsg_alloc = YYSTACK_ALLOC_MAXIMUM;
      return 1;
    }

  /* Avoid sprintf, as that infringes on the user's name space.
     Don't have undefined behavior even if the translation
     produced a string with the wrong number of "%s"s.  */
  {
    char *yyp = *yymsg;
    int yyi = 0;
    while ((*yyp = *yyformat) != '\0')
      if (*yyp == '%' && yyformat[1] == 's' && yyi < yycount)
        {
          yyp += yytnamerr (yyp, yyarg[yyi++]);
          yyformat += 2;
        }
      else
        {
          yyp++;
          yyformat++;
        }
  }
  return 0;
}
#endif /* YYERROR_VERBOSE */

/*-----------------------------------------------.
| Release the memory associated to this symbol.  |
`-----------------------------------------------*/

static void
yydestruct (const char *yymsg, int yytype, YYSTYPE *yyvaluep)
{
  YYUSE (yyvaluep);
  if (!yymsg)
    yymsg = "Deleting";
  YY_SYMBOL_PRINT (yymsg, yytype, yyvaluep, yylocationp);

  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  YYUSE (yytype);
  YY_IGNORE_MAYBE_UNINITIALIZED_END
}




/* The lookahead symbol.  */
int yychar;

/* The semantic value of the lookahead symbol.  */
YYSTYPE yylval;
/* Number of syntax errors so far.  */
int yynerrs;


/*----------.
| yyparse.  |
`----------*/

int
yyparse (void)
{
    int yystate;
    /* Number of tokens to shift before error messages enabled.  */
    int yyerrstatus;

    /* The stacks and their tools:
       'yyss': related to states.
       'yyvs': related to semantic values.

       Refer to the stacks through separate pointers, to allow yyoverflow
       to reallocate them elsewhere.  */

    /* The state stack.  */
    yytype_int16 yyssa[YYINITDEPTH];
    yytype_int16 *yyss;
    yytype_int16 *yyssp;

    /* The semantic value stack.  */
    YYSTYPE yyvsa[YYINITDEPTH];
    YYSTYPE *yyvs;
    YYSTYPE *yyvsp;

    YYSIZE_T yystacksize;

  int yyn;
  int yyresult;
  /* Lookahead token as an internal (translated) token number.  */
  int yytoken = 0;
  /* The variables used to return semantic value and location from the
     action routines.  */
  YYSTYPE yyval;

#if YYERROR_VERBOSE
  /* Buffer for error messages, and its allocated size.  */
  char yymsgbuf[128];
  char *yymsg = yymsgbuf;
  YYSIZE_T yymsg_alloc = sizeof yymsgbuf;
#endif

#define YYPOPSTACK(N)   (yyvsp -= (N), yyssp -= (N))

  /* The number of symbols on the RHS of the reduced rule.
     Keep to zero when no symbol should be popped.  */
  int yylen = 0;

  yyssp = yyss = yyssa;
  yyvsp = yyvs = yyvsa;
  yystacksize = YYINITDEPTH;

  YYDPRINTF ((stderr, "Starting parse\n"));

  yystate = 0;
  yyerrstatus = 0;
  yynerrs = 0;
  yychar = YYEMPTY; /* Cause a token to be read.  */
  goto yysetstate;

/*------------------------------------------------------------.
| yynewstate -- Push a new state, which is found in yystate.  |
`------------------------------------------------------------*/
 yynewstate:
  /* In all cases, when you get here, the value and location stacks
     have just been pushed.  So pushing a state here evens the stacks.  */
  yyssp++;

 yysetstate:
  *yyssp = yystate;

  if (yyss + yystacksize - 1 <= yyssp)
    {
      /* Get the current used size of the three stacks, in elements.  */
      YYSIZE_T yysize = yyssp - yyss + 1;

#ifdef yyoverflow
      {
        /* Give user a chance to reallocate the stack.  Use copies of
           these so that the &'s don't force the real ones into
           memory.  */
        YYSTYPE *yyvs1 = yyvs;
        yytype_int16 *yyss1 = yyss;

        /* Each stack pointer address is followed by the size of the
           data in use in that stack, in bytes.  This used to be a
           conditional around just the two extra args, but that might
           be undefined if yyoverflow is a macro.  */
        yyoverflow (YY_("memory exhausted"),
                    &yyss1, yysize * sizeof (*yyssp),
                    &yyvs1, yysize * sizeof (*yyvsp),
                    &yystacksize);

        yyss = yyss1;
        yyvs = yyvs1;
      }
#else /* no yyoverflow */
# ifndef YYSTACK_RELOCATE
      goto yyexhaustedlab;
# else
      /* Extend the stack our own way.  */
      if (YYMAXDEPTH <= yystacksize)
        goto yyexhaustedlab;
      yystacksize *= 2;
      if (YYMAXDEPTH < yystacksize)
        yystacksize = YYMAXDEPTH;

      {
        yytype_int16 *yyss1 = yyss;
        union yyalloc *yyptr =
          (union yyalloc *) YYSTACK_ALLOC (YYSTACK_BYTES (yystacksize));
        if (! yyptr)
          goto yyexhaustedlab;
        YYSTACK_RELOCATE (yyss_alloc, yyss);
        YYSTACK_RELOCATE (yyvs_alloc, yyvs);
#  undef YYSTACK_RELOCATE
        if (yyss1 != yyssa)
          YYSTACK_FREE (yyss1);
      }
# endif
#endif /* no yyoverflow */

      yyssp = yyss + yysize - 1;
      yyvsp = yyvs + yysize - 1;

      YYDPRINTF ((stderr, "Stack size increased to %lu\n",
                  (unsigned long int) yystacksize));

      if (yyss + yystacksize - 1 <= yyssp)
        YYABORT;
    }

  YYDPRINTF ((stderr, "Entering state %d\n", yystate));

  if (yystate == YYFINAL)
    YYACCEPT;

  goto yybackup;

/*-----------.
| yybackup.  |
`-----------*/
yybackup:

  /* Do appropriate processing given the current state.  Read a
     lookahead token if we need one and don't already have one.  */

  /* First try to decide what to do without reference to lookahead token.  */
  yyn = yypact[yystate];
  if (yypact_value_is_default (yyn))
    goto yydefault;

  /* Not known => get a lookahead token if don't already have one.  */

  /* YYCHAR is either YYEMPTY or YYEOF or a valid lookahead symbol.  */
  if (yychar == YYEMPTY)
    {
      YYDPRINTF ((stderr, "Reading a token: "));
      yychar = yylex ();
    }

  if (yychar <= YYEOF)
    {
      yychar = yytoken = YYEOF;
      YYDPRINTF ((stderr, "Now at end of input.\n"));
    }
  else
    {
      yytoken = YYTRANSLATE (yychar);
      YY_SYMBOL_PRINT ("Next token is", yytoken, &yylval, &yylloc);
    }

  /* If the proper action on seeing token YYTOKEN is to reduce or to
     detect an error, take that action.  */
  yyn += yytoken;
  if (yyn < 0 || YYLAST < yyn || yycheck[yyn] != yytoken)
    goto yydefault;
  yyn = yytable[yyn];
  if (yyn <= 0)
    {
      if (yytable_value_is_error (yyn))
        goto yyerrlab;
      yyn = -yyn;
      goto yyreduce;
    }

  /* Count tokens shifted since error; after three, turn off error
     status.  */
  if (yyerrstatus)
    yyerrstatus--;

  /* Shift the lookahead token.  */
  YY_SYMBOL_PRINT ("Shifting", yytoken, &yylval, &yylloc);

  /* Discard the shifted token.  */
  yychar = YYEMPTY;

  yystate = yyn;
  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  *++yyvsp = yylval;
  YY_IGNORE_MAYBE_UNINITIALIZED_END

  goto yynewstate;


/*-----------------------------------------------------------.
| yydefault -- do the default action for the current state.  |
`-----------------------------------------------------------*/
yydefault:
  yyn = yydefact[yystate];
  if (yyn == 0)
    goto yyerrlab;
  goto yyreduce;


/*-----------------------------.
| yyreduce -- Do a reduction.  |
`-----------------------------*/
yyreduce:
  /* yyn is the number of a rule to reduce with.  */
  yylen = yyr2[yyn];

  /* If YYLEN is nonzero, implement the default value of the action:
     '$$ = $1'.

     Otherwise, the following line sets YYVAL to garbage.
     This behavior is undocumented and Bison
     users should not rely upon it.  Assigning to YYVAL
     unconditionally makes the parser a bit smaller, and it avoids a
     GCC warning that YYVAL may be used uninitialized.  */
  yyval = yyvsp[1-yylen];


  YY_REDUCE_PRINT (yyn);
  switch (yyn)
    {
        case 2:
#line 167 "modelParser.y" /* yacc.c:1648  */
    {
	int mkres = mkdir(outputDir, S_IRWXU | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH);
	if(mkres < 0 && errno != EEXIST)
	{
		printf("Can not create the directory for output files.\n");
		exit(1);
	}

	mkres = mkdir(imageDir, S_IRWXU | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH);
	if(mkres < 0 && errno != EEXIST)
	{
		printf("Can not create the directory for images.\n");
		exit(1);
	}

	int result;

	clock_t begin, end;
	begin = clock();
	result = continuousProblem.run();
	end = clock();

	printf("\n");

	if(result == COMPLETED_SAFE)
	{
		printf("Computation completed: %ld flowpipe(s) computed.\n", continuousProblem.numOfFlowpipes());
	}
	else
	{
		printf(BOLD_FONT RED_COLOR "Computation not completed: %ld flowpipe(s) computed.\n" RESET_COLOR, continuousProblem.numOfFlowpipes());
		printf(BOLD_FONT "Please try smaller step sizes or larger Taylor model orders.\n" RESET_COLOR);
	}

	printf("Total time cost:" BOLD_FONT " %lf" RESET_COLOR " seconds.\n\n", (double)(end - begin) / CLOCKS_PER_SEC);

	continuousProblem.bSafetyChecking = false;

	if(continuousProblem.bPlot)
	{
		if(continuousProblem.bDump)
		{
			printf("Preparing for plotting and dumping...\n");
			continuousProblem.prepareForDumping();
			printf("Done.\n");

			continuousProblem.plot_2D(false);

			char filename[NAME_SIZE+10];
			sprintf(filename, "%s%s.flow", outputDir, continuousProblem.outputFileName);
			FILE *fpDumping = fopen(filename, "w");

			if(fpDumping == NULL)
			{
				printf("Can not create the dumping file.\n");
				exit(1);
			}

			printf("Writing the flowpipe(s)...\n");
			continuousProblem.dump(fpDumping);
			printf("Done.\n");

			fclose(fpDumping);
		}
		else
		{
			printf("Preparing for plotting...\n");
			continuousProblem.prepareForPlotting();
			printf("Done.\n");

			continuousProblem.plot_2D(true);
		}
	}
	else
	{
		if(continuousProblem.bDump)
		{
			printf("Preparing for dumping...\n");
			continuousProblem.prepareForDumping();
			printf("Done.\n");

			char filename[NAME_SIZE+10];
			sprintf(filename, "%s%s.flow", outputDir, continuousProblem.outputFileName);
			FILE *fpDumping = fopen(filename, "w");

			if(fpDumping == NULL)
			{
				printf("Can not create the dumping file.\n");
				exit(1);
			}

			printf("Writing the flowpipe(s)...\n");
			continuousProblem.dump(fpDumping);
			printf("Done.\n");

			fclose(fpDumping);
		}
	}
}
#line 2341 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 3:
#line 268 "modelParser.y" /* yacc.c:1648  */
    {
	int mkres = mkdir(outputDir, S_IRWXU | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH);
	if(mkres < 0 && errno != EEXIST)
	{
		printf("Can not create the directory for output files.\n");
		exit(1);
	}

	mkres = mkdir(imageDir, S_IRWXU | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH);
	if(mkres < 0 && errno != EEXIST)
	{
		printf("Can not create the directory for images.\n");
		exit(1);
	}

	continuousProblem.bSafetyChecking = true;

	clock_t begin, end;
	begin = clock();
	int result = continuousProblem.run();
	end = clock();

	printf("\n");

	switch(result)
	{
	case COMPLETED_UNSAFE:
		printf("Computation completed: %ld flowpipe(s) computed.\n\n", continuousProblem.numOfFlowpipes());
		printf(BOLD_FONT "Result of the safety verification on the computed flowpipes: " RESET_COLOR);
		printf(BOLD_FONT RED_COLOR "UNSAFE\n\n" RESET_COLOR);
		break;
	case COMPLETED_SAFE:
		printf("Computation completed: %ld flowpipe(s) computed.\n\n", continuousProblem.numOfFlowpipes());
		printf(BOLD_FONT "Result of the safety verification on the computed flowpipes: " RESET_COLOR);
		printf(BOLD_FONT GREEN_COLOR "SAFE\n\n" RESET_COLOR);
		break;
	case COMPLETED_UNKNOWN:
		printf("Computation completed: %ld flowpipe(s) computed.\n\n", continuousProblem.numOfFlowpipes());
		printf(BOLD_FONT "Result of the safety verification on the computed flowpipes: " RESET_COLOR);
		printf(BOLD_FONT BLUE_COLOR "UNKNOWN\n\n" RESET_COLOR);
		break;
	case UNCOMPLETED_UNSAFE:
		printf(BOLD_FONT RED_COLOR "Computation not completed: %ld flowpipe(s) computed.\n" RESET_COLOR, continuousProblem.numOfFlowpipes());
		printf(BOLD_FONT "Please try smaller step sizes or larger Taylor model orders.\n\n" RESET_COLOR);
		printf(BOLD_FONT "Result of the safety verification on the computed flowpipes: " RESET_COLOR);
		printf(BOLD_FONT RED_COLOR "UNSAFE\n\n" RESET_COLOR);
		break;
	case UNCOMPLETED_SAFE:
		printf(BOLD_FONT RED_COLOR "Computation not completed: %ld flowpipe(s) computed.\n" RESET_COLOR, continuousProblem.numOfFlowpipes());
		printf(BOLD_FONT "Please try smaller step sizes or larger Taylor model orders.\n\n" RESET_COLOR);
		printf(BOLD_FONT "Result of the safety verification on the computed flowpipes: " RESET_COLOR);
		printf(BOLD_FONT GREEN_COLOR "SAFE\n\n" RESET_COLOR);
		break;
	case UNCOMPLETED_UNKNOWN:
		printf(BOLD_FONT RED_COLOR "Computation not completed: %ld flowpipe(s) computed.\n" RESET_COLOR, continuousProblem.numOfFlowpipes());
		printf(BOLD_FONT "Please try smaller step sizes or larger Taylor model orders.\n\n" RESET_COLOR);
		printf(BOLD_FONT "Result of the safety verification on the computed flowpipes: " RESET_COLOR);
		printf(BOLD_FONT BLUE_COLOR "UNKNOWN\n\n" RESET_COLOR);
		break;
	}

	printf("Total time cost:" BOLD_FONT " %lf" RESET_COLOR " seconds.\n\n", (double)(end - begin) / CLOCKS_PER_SEC);

	if(continuousProblem.bPlot)
	{
		if(continuousProblem.bDump)
		{
			printf("Preparing for plotting and dumping...\n");
			continuousProblem.prepareForDumping();
			printf("Done.\n");

			continuousProblem.plot_2D(false);

			char filename[NAME_SIZE+10];
			sprintf(filename, "%s%s.flow", outputDir, continuousProblem.outputFileName);
			FILE *fpDumping = fopen(filename, "w");

			if(fpDumping == NULL)
			{
				printf("Can not create the dumping file.\n");
				exit(1);
			}

			printf("Writing the flowpipe(s)...\n");
			continuousProblem.dump(fpDumping);
			printf("Done.\n");

			fclose(fpDumping);
		}
		else
		{
			printf("Preparing for plotting...\n");
			continuousProblem.prepareForPlotting();
			printf("Done.\n");

			continuousProblem.plot_2D(true);
		}
	}
	else
	{
		if(continuousProblem.bDump)
		{
			printf("Preparing for dumping...\n");
			continuousProblem.prepareForDumping();
			printf("Done.\n");

			char filename[NAME_SIZE+10];
			sprintf(filename, "%s%s.flow", outputDir, continuousProblem.outputFileName);
			FILE *fpDumping = fopen(filename, "w");

			if(fpDumping == NULL)
			{
				printf("Can not create the dumping file.\n");
				exit(1);
			}

			printf("Writing the flowpipe(s)...\n");
			continuousProblem.dump(fpDumping);
			printf("Done.\n");

			fclose(fpDumping);
		}
	}
}
#line 2470 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 4:
#line 394 "modelParser.y" /* yacc.c:1648  */
    {
	int mkres = mkdir(outputDir, S_IRWXU | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH);
	if(mkres < 0 && errno != EEXIST)
	{
		printf("Can not create the directory for output files.\n");
		exit(1);
	}

	mkres = mkdir(imageDir, S_IRWXU | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH);
	if(mkres < 0 && errno != EEXIST)
	{
		printf("Can not create the directory for images.\n");
		exit(1);
	}

	int result;

	clock_t begin, end;
	begin = clock();
	result = hybridProblem.run();
	end = clock();

	printf("\n");

	if(result == COMPLETED_SAFE)
	{
		printf("Computation completed: %ld flowpipe(s) computed.\n", hybridProblem.numOfFlowpipes());
	}
	else
	{
		printf(BOLD_FONT RED_COLOR "Computation not completed: %ld flowpipe(s) computed.\n" RESET_COLOR, hybridProblem.numOfFlowpipes());
		printf(BOLD_FONT "Please try smaller step sizes or larger Taylor model orders.\n" RESET_COLOR);
	}

	printf("Time cost of flowpipe construction:" BOLD_FONT " %lf" RESET_COLOR " seconds.\n\n", (double)(end - begin) / CLOCKS_PER_SEC);

	hybridProblem.bSafetyChecking = false;

	if(hybridProblem.bPlot)
	{
		if(hybridProblem.bDump)
		{
			printf("Preparing for plotting and dumping...\n");
			hybridProblem.prepareForDumping();
			printf("Done.\n");

			hybridProblem.plot_2D(false);

			char filename[NAME_SIZE+10];
			sprintf(filename, "%s%s.flow", outputDir, hybridProblem.outputFileName);
			FILE *fpDumping = fopen(filename, "w");

			if(fpDumping == NULL)
			{
				printf("Can not create the dumping file.\n");
				exit(1);
			}

			printf("Writing the flowpipe(s)...\n");
			hybridProblem.dump(fpDumping);
			printf("Done.\n");

			fclose(fpDumping);
		}
		else
		{
			printf("Preparing for plotting...\n");
			hybridProblem.prepareForPlotting();
			printf("Done.\n");

			hybridProblem.plot_2D(true);
		}
	}
	else
	{
		if(hybridProblem.bDump)
		{
			printf("Preparing for dumping...\n");
			hybridProblem.prepareForDumping();
			printf("Done.\n");

			char filename[NAME_SIZE+10];
			sprintf(filename, "%s%s.flow", outputDir, hybridProblem.outputFileName);
			FILE *fpDumping = fopen(filename, "w");

			if(fpDumping == NULL)
			{
				printf("Can not create the dumping file.\n");
				exit(1);
			}

			printf("Writing the flowpipe(s)...\n");
			hybridProblem.dump(fpDumping);
			printf("Done.\n");

			fclose(fpDumping);
		}
	}
}
#line 2574 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 5:
#line 495 "modelParser.y" /* yacc.c:1648  */
    {
	int mkres = mkdir(outputDir, S_IRWXU | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH);
	if(mkres < 0 && errno != EEXIST)
	{
		printf("Can not create the directory for output files.\n");
		exit(1);
	}

	mkres = mkdir(imageDir, S_IRWXU | S_IRGRP | S_IXGRP | S_IROTH | S_IXOTH);
	if(mkres < 0 && errno != EEXIST)
	{
		printf("Can not create the directory for images.\n");
		exit(1);
	}

	hybridProblem.bSafetyChecking = true;

	int result;

	clock_t begin, end;
	begin = clock();
	result = hybridProblem.run();
	end = clock();

	printf("\n");

	switch(result)
	{
	case COMPLETED_UNSAFE:
		printf("Computation completed: %ld flowpipe(s) computed.\n\n", hybridProblem.numOfFlowpipes());
		printf(BOLD_FONT "Result of the safety verification on the computed flowpipes: " RESET_COLOR);
		printf(BOLD_FONT RED_COLOR "UNSAFE\n\n" RESET_COLOR);
		break;
	case COMPLETED_SAFE:
		printf("Computation completed: %ld flowpipe(s) computed.\n\n", hybridProblem.numOfFlowpipes());
		printf(BOLD_FONT "Result of the safety verification on the computed flowpipes: " RESET_COLOR);
		printf(BOLD_FONT GREEN_COLOR "SAFE\n\n" RESET_COLOR);
		break;
	case COMPLETED_UNKNOWN:
		printf("Computation completed: %ld flowpipe(s) computed.\n\n", hybridProblem.numOfFlowpipes());
		printf(BOLD_FONT "Result of the safety verification on the computed flowpipes: " RESET_COLOR);
		printf(BOLD_FONT BLUE_COLOR "UNKNOWN\n\n" RESET_COLOR);
		break;
	case UNCOMPLETED_UNSAFE:
		printf(BOLD_FONT RED_COLOR "Computation not completed: %ld flowpipe(s) computed.\n" RESET_COLOR, hybridProblem.numOfFlowpipes());
		printf(BOLD_FONT "Please try smaller step sizes or larger Taylor model orders.\n\n" RESET_COLOR);
		printf(BOLD_FONT "Result of the safety verification on the computed flowpipes: " RESET_COLOR);
		printf(BOLD_FONT RED_COLOR "UNSAFE\n\n" RESET_COLOR);
		break;
	case UNCOMPLETED_SAFE:
		printf(BOLD_FONT RED_COLOR "Computation not completed: %ld flowpipe(s) computed.\n" RESET_COLOR, hybridProblem.numOfFlowpipes());
		printf(BOLD_FONT "Please try smaller step sizes or larger Taylor model orders.\n\n" RESET_COLOR);
		printf(BOLD_FONT "Result of the safety verification on the computed flowpipes: " RESET_COLOR);
		printf(BOLD_FONT GREEN_COLOR "SAFE\n\n" RESET_COLOR);
		break;
	case UNCOMPLETED_UNKNOWN:
		printf(BOLD_FONT RED_COLOR "Computation not completed: %ld flowpipe(s) computed.\n" RESET_COLOR, hybridProblem.numOfFlowpipes());
		printf(BOLD_FONT "Please try smaller step sizes or larger Taylor model orders.\n\n" RESET_COLOR);
		printf(BOLD_FONT "Result of the safety verification on the computed flowpipes: " RESET_COLOR);
		printf(BOLD_FONT BLUE_COLOR "UNKNOWN\n\n" RESET_COLOR);
		break;
	}

	printf("Total time cost:" BOLD_FONT " %lf" RESET_COLOR " seconds.\n\n", (double)(end - begin) / CLOCKS_PER_SEC);

	if(hybridProblem.bPlot)
	{
		if(hybridProblem.bDump)
		{
			printf("Preparing for plotting and dumping...\n");
			hybridProblem.prepareForDumping();
			printf("Done.\n");

			hybridProblem.plot_2D(false);

			char filename[NAME_SIZE+10];
			sprintf(filename, "%s%s.flow", outputDir, hybridProblem.outputFileName);
			FILE *fpDumping = fopen(filename, "w");

			if(fpDumping == NULL)
			{
				printf("Can not create the dumping file.\n");
				exit(1);
			}

			printf("Writing the flowpipe(s)...\n");
			hybridProblem.dump(fpDumping);
			printf("Done.\n");

			fclose(fpDumping);
		}
		else
		{
			printf("Preparing for plotting...\n");
			hybridProblem.prepareForPlotting();
			printf("Done.\n");

			hybridProblem.plot_2D(true);
		}
	}
	else
	{
		if(hybridProblem.bDump)
		{
			printf("Preparing for dumping...\n");
			hybridProblem.prepareForDumping();
			printf("Done.\n");

			char filename[NAME_SIZE+10];
			sprintf(filename, "%s%s.flow", outputDir, hybridProblem.outputFileName);
			FILE *fpDumping = fopen(filename, "w");

			if(fpDumping == NULL)
			{
				printf("Can not create the dumping file.\n");
				exit(1);
			}

			printf("Writing the flowpipe(s)...\n");
			hybridProblem.dump(fpDumping);
			printf("Done.\n");

			fclose(fpDumping);
		}
	}
}
#line 2705 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 6:
#line 623 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-9].dblVal) <= 0)
	{
		parseError("The cutoff threshold should be a positive number.", lineNum);
		exit(1);
	}

	continuousProblem.globalMaxOrder = (int)(yyvsp[-9].dblVal);

	flowstar::Interval I(-(yyvsp[-7].dblVal),(yyvsp[-7].dblVal));
	continuousProblem.cutoff_threshold = I;

	clock_t begin, end;
	int checkingResult;
	printf("Safety checking ...\n");
	begin = clock();
	checkingResult = continuousProblem.safetyChecking();
	end = clock();
	printf("Done.\n");
	printf("Time cost of safety verification:" BOLD_FONT " %lf" RESET_COLOR " seconds.\n\n", (double)(end - begin) / CLOCKS_PER_SEC);
	printf(BOLD_FONT "Result of safety verification: " RESET_COLOR);

	switch(checkingResult)
	{
	case UNSAFE:
		printf(BOLD_FONT RED_COLOR "UNSAFE\n\n" RESET_COLOR);
		break;
	case SAFE:
		printf(BOLD_FONT GREEN_COLOR "SAFE\n\n" RESET_COLOR);
		break;
	case UNKNOWN:
		printf(BOLD_FONT BLUE_COLOR "UNKNOWN\n\n" RESET_COLOR);
		break;
	}

	if(continuousProblem.bPlot)
	{
		continuousProblem.plot_2D(false);
	}
}
#line 2750 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 7:
#line 665 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-6].dblVal) <= 0)
	{
		parseError("The cutoff threshold should be a positive number.", lineNum);
		exit(1);
	}

	continuousProblem.globalMaxOrder = (int)(yyvsp[-8].dblVal);

	flowstar::Interval I(-(yyvsp[-6].dblVal),(yyvsp[-6].dblVal));
	continuousProblem.cutoff_threshold = I;

	if(continuousProblem.bPlot)
	{
		continuousProblem.plot_2D(false);
	}
}
#line 2772 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 8:
#line 684 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-13].dblVal) <= 0)
	{
		parseError("The cutoff threshold should be a positive number.", lineNum);
		exit(1);
	}

	continuousProblem.step = (yyvsp[-17].dblVal);
	continuousProblem.globalMaxOrder = (int)(yyvsp[-15].dblVal);

	flowstar::Interval I(-(yyvsp[-13].dblVal),(yyvsp[-13].dblVal));
	continuousProblem.cutoff_threshold = I;

	if(continuousProblem.bPlot)
	{
		continuousProblem.plot_2D(false);
	}
}
#line 2795 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 9:
#line 704 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-14].dblVal) <= 0)
	{
		parseError("The cutoff threshold should be a positive number.", lineNum);
		exit(1);
	}

	continuousProblem.step = (yyvsp[-18].dblVal);
	continuousProblem.globalMaxOrder = (int)(yyvsp[-16].dblVal);

	flowstar::Interval I(-(yyvsp[-14].dblVal),(yyvsp[-14].dblVal));
	continuousProblem.cutoff_threshold = I;

	clock_t begin, end;
	int checkingResult;
	printf("Safety checking ...\n");
	begin = clock();
	checkingResult = continuousProblem.safetyChecking();
	end = clock();
	printf("Done.\n");
	printf("Time cost of safety verification:" BOLD_FONT " %lf" RESET_COLOR " seconds.\n\n", (double)(end - begin) / CLOCKS_PER_SEC);
	printf(BOLD_FONT "Result of safety verification: " RESET_COLOR);

	switch(checkingResult)
	{
	case UNSAFE:
		printf(BOLD_FONT RED_COLOR "UNSAFE\n\n" RESET_COLOR);
		break;
	case SAFE:
		printf(BOLD_FONT GREEN_COLOR "SAFE\n\n" RESET_COLOR);
		break;
	case UNKNOWN:
		printf(BOLD_FONT BLUE_COLOR "UNKNOWN\n\n" RESET_COLOR);
		break;
	}

	if(continuousProblem.bPlot)
	{
		continuousProblem.plot_2D(false);
	}
}
#line 2841 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 10:
#line 747 "modelParser.y" /* yacc.c:1648  */
    {
	clock_t begin, end;

	generateNodeSeq(hybridProblem.traceNodes, hybridProblem.traceTree);

	int checkingResult;
	printf("Safety checking ...\n");
	begin = clock();
	checkingResult = hybridProblem.safetyChecking();
	end = clock();
	printf("Done.\n");
	printf("Time cost of safety verification:" BOLD_FONT " %lf" RESET_COLOR " seconds.\n\n", (double)(end - begin) / CLOCKS_PER_SEC);
	printf(BOLD_FONT "Result of safety verification: " RESET_COLOR);

	switch(checkingResult)
	{
	case UNSAFE:
		printf(BOLD_FONT RED_COLOR "UNSAFE\n\n" RESET_COLOR);
		break;
	case SAFE:
		printf(BOLD_FONT GREEN_COLOR "SAFE\n\n" RESET_COLOR);
		break;
	case UNKNOWN:
		printf(BOLD_FONT BLUE_COLOR "UNKNOWN\n\n" RESET_COLOR);
		break;
	}

	if(hybridProblem.bPlot)
	{
		hybridProblem.plot_2D(false);
	}
}
#line 2878 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 11:
#line 781 "modelParser.y" /* yacc.c:1648  */
    {
	if(hybridProblem.bPlot)
	{
		hybridProblem.plot_2D(false);
	}
}
#line 2889 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 12:
#line 789 "modelParser.y" /* yacc.c:1648  */
    {
	(yyvsp[-1].ptm)->getExpansion(parseResult.expansion);
	parseResult.remainder = (yyvsp[-1].ptm)->getRemainder();
	delete (yyvsp[-1].ptm);
}
#line 2899 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 13:
#line 796 "modelParser.y" /* yacc.c:1648  */
    {
	parseResult.remainder = (*(yyvsp[-1].pint));
	delete (yyvsp[-1].pint);
}
#line 2908 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 14:
#line 802 "modelParser.y" /* yacc.c:1648  */
    {
	parseResult.expansion = (*(yyvsp[-1].poly));
	delete (yyvsp[-1].poly);
}
#line 2917 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 15:
#line 808 "modelParser.y" /* yacc.c:1648  */
    {
	parseResult.strExpansion = (yyvsp[-1].p_ODE_String)->ode;
	parseResult.constant = (yyvsp[-1].p_ODE_String)->constant;
	delete (yyvsp[-1].p_ODE_String);
}
#line 2927 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 16:
#line 815 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::up_parseresult = (*(yyvsp[-1].pUpoly));
	delete (yyvsp[-1].pUpoly);
}
#line 2936 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 17:
#line 822 "modelParser.y" /* yacc.c:1648  */
    {
	strcpy(continuousProblem.outputFileName, (yyvsp[0].identifier)->c_str());
	strcpy(hybridProblem.outputFileName, (yyvsp[0].identifier)->c_str());
	continuousProblem.bDump = true;
	continuousProblem.bPlot = true;
	hybridProblem.bDump = true;
	hybridProblem.bPlot = true;
}
#line 2949 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 18:
#line 832 "modelParser.y" /* yacc.c:1648  */
    {
	strcpy(continuousProblem.outputFileName, (yyvsp[0].identifier)->c_str());
	strcpy(hybridProblem.outputFileName, (yyvsp[0].identifier)->c_str());
	continuousProblem.bDump = false;
	continuousProblem.bPlot = true;
	hybridProblem.bDump = false;
	hybridProblem.bPlot = true;
}
#line 2962 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 19:
#line 842 "modelParser.y" /* yacc.c:1648  */
    {
	strcpy(continuousProblem.outputFileName, (yyvsp[0].identifier)->c_str());
	strcpy(hybridProblem.outputFileName, (yyvsp[0].identifier)->c_str());
	continuousProblem.bDump = true;
	continuousProblem.bPlot = false;
	hybridProblem.bDump = true;
	hybridProblem.bPlot = false;
}
#line 2975 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 20:
#line 852 "modelParser.y" /* yacc.c:1648  */
    {
	continuousProblem.bDump = false;
	continuousProblem.bPlot = false;
	hybridProblem.bDump = false;
	hybridProblem.bPlot = false;
}
#line 2986 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 21:
#line 861 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 2993 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 22:
#line 866 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 3000 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 23:
#line 871 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.intVal) = 1;
}
#line 3008 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 24:
#line 876 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.intVal) = 0;
}
#line 3016 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 25:
#line 880 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.intVal) = 0;
}
#line 3024 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 26:
#line 887 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::domainVarNames = varlist.varNames;
}
#line 3032 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 27:
#line 893 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 3039 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 28:
#line 898 "modelParser.y" /* yacc.c:1648  */
    {
	continuousProblem.flowpipesCompo.push_back(*(yyvsp[-3].tmVec));
	continuousProblem.domains.push_back(*(yyvsp[-2].intVec));
	continuousProblem.flowpipes_safety.push_back(SAFE);

	if((yyvsp[-1].intVal) == 1)
	{
		continuousProblem.flowpipes_contracted.push_back(true);
	}
	else
	{
		continuousProblem.flowpipes_contracted.push_back(false);
	}

	delete (yyvsp[-3].tmVec);
	delete (yyvsp[-2].intVec);
}
#line 3061 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 29:
#line 917 "modelParser.y" /* yacc.c:1648  */
    {
	continuousProblem.flowpipesCompo.push_back(*(yyvsp[-3].tmVec));
	continuousProblem.domains.push_back(*(yyvsp[-2].intVec));
	continuousProblem.flowpipes_safety.push_back(SAFE);

	if((yyvsp[-1].intVal) == 1)
	{
		continuousProblem.flowpipes_contracted.push_back(true);
	}
	else
	{
		continuousProblem.flowpipes_contracted.push_back(false);
	}

	delete (yyvsp[-3].tmVec);
	delete (yyvsp[-2].intVec);
}
#line 3083 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 30:
#line 938 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Flowpipe initialSet;

	initialSet.tmvPre = *(yyvsp[-2].tmVec);
	initialSet.domain = *(yyvsp[-1].intVec);

	continuousProblem.system.initialSets.push_back(initialSet);

	delete (yyvsp[-2].tmVec);
	delete (yyvsp[-1].intVec);
}
#line 3099 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 31:
#line 951 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Flowpipe initialSet;

	initialSet.tmvPre = *(yyvsp[-2].tmVec);
	initialSet.domain = *(yyvsp[-1].intVec);

	continuousProblem.system.initialSets.push_back(initialSet);

	delete (yyvsp[-2].tmVec);
	delete (yyvsp[-1].intVec);
}
#line 3115 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 32:
#line 965 "modelParser.y" /* yacc.c:1648  */
    {
	continuousProblem.flowpipesCompo.push_back(*(yyvsp[-1].tmVec));
	int num = continuousProblem.system.initialSets.size();

	for(int i=0; i<num; ++i)
	{
		continuousProblem.flowpipes_safety.push_back(SAFE);
	}

	delete (yyvsp[-1].tmVec);
}
#line 3131 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 33:
#line 978 "modelParser.y" /* yacc.c:1648  */
    {
	continuousProblem.flowpipesCompo.push_back(*(yyvsp[-1].tmVec));

	int num = continuousProblem.system.initialSets.size();

	for(int i=0; i<num; ++i)
	{
		continuousProblem.flowpipes_safety.push_back(SAFE);
	}

	delete (yyvsp[-1].tmVec);
}
#line 3148 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 34:
#line 994 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::TaylorModelVec tmvDummy;

	if((yyvsp[-9].dblVal) <= 0)
	{
		parseError("The order should be a positive number.", lineNum);
		exit(1);
	}

	if((yyvsp[-5].dblVal) <= 0)
	{
		parseError("The cutoff threshold should be a positive number.", lineNum);
		exit(1);
	}

	flowstar::Interval I(-(yyvsp[-5].dblVal),(yyvsp[-5].dblVal));
	mode_local_setting.cutoff_threshold = I;
	mode_local_setting.globalMaxOrder = (yyvsp[-9].dblVal);

	hybridProblem.declareMode(*(yyvsp[-13].identifier), tmvDummy, *(yyvsp[-2].vecConstraints), 0, mode_local_setting);

	delete (yyvsp[-13].identifier);
	delete (yyvsp[-2].vecConstraints);
}
#line 3177 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 35:
#line 1020 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::TaylorModelVec tmvDummy;

	if((yyvsp[-9].dblVal) <= 0)
	{
		parseError("The order should be a positive number.", lineNum);
		exit(1);
	}

	if((yyvsp[-5].dblVal) <= 0)
	{
		parseError("The cutoff threshold should be a positive number.", lineNum);
		exit(1);
	}

	flowstar::Interval I(-(yyvsp[-5].dblVal),(yyvsp[-5].dblVal));
	mode_local_setting.cutoff_threshold = I;
	mode_local_setting.globalMaxOrder = (yyvsp[-9].dblVal);

	hybridProblem.declareMode(*(yyvsp[-13].identifier), tmvDummy, *(yyvsp[-2].vecConstraints), 0, mode_local_setting);

	delete (yyvsp[-13].identifier);
	delete (yyvsp[-2].vecConstraints);
}
#line 3206 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 36:
#line 1047 "modelParser.y" /* yacc.c:1648  */
    {
	int id = hybridProblem.getIDForMode(*(yyvsp[-4].identifier));
	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "Mode %s has not been declared.", (*(yyvsp[-4].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	hybridProblem.modeIDs.push_back(id);
	hybridProblem.flowpipes.push_back(continuousProblem.flowpipesCompo);
	hybridProblem.domains.push_back(continuousProblem.domains);
	hybridProblem.flowpipes_safety.push_back(continuousProblem.flowpipes_safety);
	hybridProblem.flowpipes_contracted.push_back(continuousProblem.flowpipes_contracted);

	continuousProblem.flowpipesCompo.clear();
	continuousProblem.domains.clear();
	continuousProblem.flowpipes_contracted.clear();
	continuousProblem.flowpipes_safety.clear();
	continuousProblem.tmVarTab.clear();
	continuousProblem.tmVarNames.clear();
}
#line 3234 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 37:
#line 1072 "modelParser.y" /* yacc.c:1648  */
    {
	int id = hybridProblem.getIDForMode(*(yyvsp[-4].identifier));
	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "Mode %s has not been declared.", (*(yyvsp[-4].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	hybridProblem.modeIDs.push_back(id);
	hybridProblem.flowpipes.push_back(continuousProblem.flowpipesCompo);
	hybridProblem.domains.push_back(continuousProblem.domains);
	hybridProblem.flowpipes_safety.push_back(continuousProblem.flowpipes_safety);
	hybridProblem.flowpipes_contracted.push_back(continuousProblem.flowpipes_contracted);

	continuousProblem.flowpipesCompo.clear();
	continuousProblem.domains.clear();
	continuousProblem.flowpipes_contracted.clear();
	continuousProblem.flowpipes_safety.clear();
	continuousProblem.tmVarTab.clear();
	continuousProblem.tmVarNames.clear();
}
#line 3262 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 38:
#line 1098 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 3269 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 39:
#line 1102 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 3276 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 40:
#line 1107 "modelParser.y" /* yacc.c:1648  */
    {
	int id = hybridProblem.getIDForMode(*(yyvsp[0].identifier));
	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "Mode %s has not been declared.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	std::list<flowstar::TreeNode *>::iterator iter = (yyval.pNode)->children.begin();
	bool found = false;
	for(; iter!=(yyval.pNode)->children.end(); ++iter)
	{
		if((*iter)->jumpID == (yyvsp[-10].dblVal) && (*iter)->modeID == id)
		{
			(yyval.pNode) = *iter;
			found = true;
			break;
		}
	}

	if(!found)
	{
		flowstar::Interval I((yyvsp[-7].dblVal), (yyvsp[-5].dblVal));
		flowstar::TreeNode *tmp = new flowstar::TreeNode((int)(yyvsp[-10].dblVal), id, I);
		tmp->parent = (yyval.pNode);
		(yyval.pNode)->children.push_back(tmp);
		(yyval.pNode) = tmp;
	}

	delete (yyvsp[0].identifier);
}
#line 3314 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 41:
#line 1142 "modelParser.y" /* yacc.c:1648  */
    {
	int id = hybridProblem.getIDForMode(*(yyvsp[0].identifier));
	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "Mode %s has not been declared.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	if(hybridProblem.traceTree == NULL)
	{
		flowstar::Interval intZero;
		hybridProblem.traceTree = new flowstar::TreeNode(0, id, intZero);
		(yyval.pNode) = hybridProblem.traceTree;
	}
	else
	{
		if(hybridProblem.traceTree->modeID == id)
		{
			(yyval.pNode) = hybridProblem.traceTree;
		}
		else
		{
			parseError("Invalid computation path.", lineNum);
			exit(1);
		}
	}

	delete (yyvsp[0].identifier);
}
#line 3350 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 42:
#line 1176 "modelParser.y" /* yacc.c:1648  */
    {
	continuousProblem.bPrint = true;
	hybridProblem.bPrint = true;
}
#line 3359 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 43:
#line 1182 "modelParser.y" /* yacc.c:1648  */
    {
	continuousProblem.bPrint = false;
	hybridProblem.bPrint = false;
}
#line 3368 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 44:
#line 1189 "modelParser.y" /* yacc.c:1648  */
    {
	continuousProblem.unsafeSet = *(yyvsp[-1].vecConstraints);
	delete (yyvsp[-1].vecConstraints);
}
#line 3377 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 45:
#line 1196 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 3384 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 46:
#line 1201 "modelParser.y" /* yacc.c:1648  */
    {
	int id = hybridProblem.getIDForMode(*(yyvsp[-3].identifier));
	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "Mode %s has not been declared.", (*(yyvsp[-3].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	hybridProblem.unsafeSet[id] = *(yyvsp[-1].vecConstraints);
	hybridProblem.bVecUnderCheck[id] = true;
	delete (yyvsp[-1].vecConstraints);
}
#line 3403 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 47:
#line 1216 "modelParser.y" /* yacc.c:1648  */
    {
	std::vector<flowstar::PolynomialConstraint> vecEmpty;
	for(int i=0; i<hybridProblem.modeNames.size(); ++i)
	{
		hybridProblem.unsafeSet.push_back(vecEmpty);
		hybridProblem.bVecUnderCheck.push_back(false);
	}
}
#line 3416 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 48:
#line 1227 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-2].poly)->degree() < 1)
	{
		parseError("Invalid constraint.", lineNum);
		exit(1);
	}

	(yyval.vecConstraints) = (yyvsp[-3].vecConstraints);
	flowstar::Interval B((yyvsp[0].dblVal));
	flowstar::PolynomialConstraint pc(*(yyvsp[-2].poly), B);
	(yyval.vecConstraints)->push_back(pc);

	delete (yyvsp[-2].poly);
}
#line 3435 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 49:
#line 1243 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-2].poly)->degree() < 1)
	{
		parseError("Invalid constraint.", lineNum);
		exit(1);
	}

	(yyval.vecConstraints) = (yyvsp[-3].vecConstraints);
	flowstar::Interval I(-1);
	(yyvsp[-2].poly)->mul_assign(I);

	flowstar::Interval B(-(yyvsp[0].dblVal));
	flowstar::PolynomialConstraint pc(*(yyvsp[-2].poly), B);
	(yyval.vecConstraints)->push_back(pc);

	delete (yyvsp[-2].poly);
}
#line 3457 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 50:
#line 1262 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-2].poly)->degree() < 1)
	{
		parseError("Invalid constraint.", lineNum);
		exit(1);
	}

	(yyval.vecConstraints) = (yyvsp[-3].vecConstraints);
	flowstar::Interval B((yyvsp[0].dblVal));
	flowstar::PolynomialConstraint pc1(*(yyvsp[-2].poly), B);
	(yyval.vecConstraints)->push_back(pc1);

	flowstar::Interval I(-1);
	(yyvsp[-2].poly)->mul_assign(I);
	flowstar::Interval mB(-(yyvsp[0].dblVal));
	flowstar::PolynomialConstraint pc2(*(yyvsp[-2].poly), mB);
	(yyval.vecConstraints)->push_back(pc2);

	delete (yyvsp[-2].poly);
}
#line 3482 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 51:
#line 1284 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-6].poly)->degree() < 1)
	{
		parseError("Invalid constraint.", lineNum);
		exit(1);
	}

	flowstar::PolynomialConstraint pc1(*(yyvsp[-6].poly), (yyvsp[-1].dblVal));
	(yyval.vecConstraints)->push_back(pc1);

	flowstar::Interval I(-1);
	(yyvsp[-6].poly)->mul_assign(I);
	flowstar::PolynomialConstraint pc2(*(yyvsp[-6].poly), -(yyvsp[-3].dblVal));
	(yyval.vecConstraints)->push_back(pc2);

	delete (yyvsp[-6].poly);
}
#line 3504 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 52:
#line 1303 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-2].poly)->degree() < 1)
	{
		parseError("Invalid constraint.", lineNum);
		exit(1);
	}

	int id = continuousProblem.getIDForPar(*(yyvsp[0].identifier));
	flowstar::Interval range;

	if(id >= 0)
	{
		continuousProblem.getRangeForPar(range, *(yyvsp[0].identifier));
	}
	else
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "Parameter %s is not declared.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	(yyval.vecConstraints) = (yyvsp[-3].vecConstraints);
	flowstar::PolynomialConstraint pc(*(yyvsp[-2].poly), range);
	(yyval.vecConstraints)->push_back(pc);

	delete (yyvsp[-2].poly);
	delete (yyvsp[0].identifier);
}
#line 3538 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 53:
#line 1334 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-2].poly)->degree() < 1)
	{
		parseError("Invalid constraint.", lineNum);
		exit(1);
	}

	int id = continuousProblem.getIDForPar(*(yyvsp[0].identifier));
	flowstar::Interval range;

	if(id >= 0)
	{
		continuousProblem.getRangeForPar(range, *(yyvsp[0].identifier));
	}
	else
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "Parameter %s is not declared.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	(yyval.vecConstraints) = (yyvsp[-3].vecConstraints);
	flowstar::Interval I(-1);
	(yyvsp[-2].poly)->mul_assign(I);
	range *= I;
	flowstar::PolynomialConstraint pc(*(yyvsp[-2].poly), range);
	(yyval.vecConstraints)->push_back(pc);

	delete (yyvsp[-2].poly);
	delete (yyvsp[0].identifier);
}
#line 3575 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 54:
#line 1368 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-2].poly)->degree() < 1)
	{
		parseError("Invalid constraint.", lineNum);
		exit(1);
	}

	int id = continuousProblem.getIDForPar(*(yyvsp[0].identifier));
	flowstar::Interval range;

	if(id >= 0)
	{
		continuousProblem.getRangeForPar(range, *(yyvsp[0].identifier));
	}
	else
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "Parameter %s is not declared.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	(yyval.vecConstraints) = (yyvsp[-3].vecConstraints);
	flowstar::PolynomialConstraint pc1(*(yyvsp[-2].poly), range);
	(yyval.vecConstraints)->push_back(pc1);

	flowstar::Interval I(-1);
	(yyvsp[-2].poly)->mul_assign(I);
	range *= I;
	flowstar::PolynomialConstraint pc2(*(yyvsp[-2].poly), range);
	(yyval.vecConstraints)->push_back(pc2);

	delete (yyvsp[-2].poly);
	delete (yyvsp[0].identifier);
}
#line 3615 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 55:
#line 1405 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-6].poly)->degree() < 1)
	{
		parseError("Invalid constraint.", lineNum);
		exit(1);
	}

	int id = continuousProblem.getIDForPar(*(yyvsp[-1].identifier));
	flowstar::Interval range;

	if(id >= 0)
	{
		continuousProblem.getRangeForPar(range, *(yyvsp[-1].identifier));
	}
	else
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "Parameter %s is not declared.", (*(yyvsp[-1].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	flowstar::PolynomialConstraint pc1(*(yyvsp[-6].poly), range);
	(yyval.vecConstraints)->push_back(pc1);

	id = continuousProblem.getIDForPar(*(yyvsp[-3].identifier));

	if(id >= 0)
	{
		continuousProblem.getRangeForPar(range, *(yyvsp[-3].identifier));
	}
	else
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "Parameter %s is not declared.", (*(yyvsp[-3].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	flowstar::Interval I(-1);
	(yyvsp[-6].poly)->mul_assign(I);
	range *= I;
	flowstar::PolynomialConstraint pc2(*(yyvsp[-6].poly), range);
	(yyval.vecConstraints)->push_back(pc2);

	delete (yyvsp[-6].poly);
	delete (yyvsp[-3].identifier);
	delete (yyvsp[-1].identifier);
}
#line 3669 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 56:
#line 1455 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.vecConstraints) = new std::vector<flowstar::PolynomialConstraint>(0);
}
#line 3677 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 57:
#line 1699 "modelParser.y" /* yacc.c:1648  */
    {
	if(initialSets.size() > 0)
	{
		flowstar::ContinuousSystem system(*(yyvsp[-5].tmVec), initialSets);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = ONLY_PICARD;
	}
	else
	{
		std::vector<flowstar::Flowpipe> vecFpTemp;
		vecFpTemp.push_back(*(yyvsp[-1].pFlowpipe));
		flowstar::ContinuousSystem system(*(yyvsp[-5].tmVec), vecFpTemp);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = ONLY_PICARD;

		delete (yyvsp[-1].pFlowpipe);
	}

	delete (yyvsp[-5].tmVec);
}
#line 3702 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 58:
#line 1721 "modelParser.y" /* yacc.c:1648  */
    {
	if(initialSets.size() > 0)
	{
		flowstar::ContinuousSystem system(*(yyvsp[-5].tmVec), initialSets);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = LOW_DEGREE;
	}
	else
	{
		std::vector<flowstar::Flowpipe> vecFpTemp;
		vecFpTemp.push_back(*(yyvsp[-1].pFlowpipe));
		flowstar::ContinuousSystem system(*(yyvsp[-5].tmVec), vecFpTemp);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = LOW_DEGREE;

		delete (yyvsp[-1].pFlowpipe);
	}

	delete (yyvsp[-5].tmVec);
}
#line 3727 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 59:
#line 1743 "modelParser.y" /* yacc.c:1648  */
    {
	if(initialSets.size() > 0)
	{
		flowstar::ContinuousSystem system(*(yyvsp[-5].tmVec), initialSets);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = HIGH_DEGREE;
	}
	else
	{
		std::vector<flowstar::Flowpipe> vecFpTemp;
		vecFpTemp.push_back(*(yyvsp[-1].pFlowpipe));
		flowstar::ContinuousSystem system(*(yyvsp[-5].tmVec), vecFpTemp);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = HIGH_DEGREE;

		delete (yyvsp[-1].pFlowpipe);
	}

	delete (yyvsp[-5].tmVec);
}
#line 3752 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 60:
#line 1765 "modelParser.y" /* yacc.c:1648  */
    {
	if(initialSets.size() > 0)
	{
		flowstar::ContinuousSystem system(*(yyvsp[-5].strVec), initialSets);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = NONPOLY_TAYLOR;
	}
	else
	{
		std::vector<flowstar::Flowpipe> vecFpTemp;
		vecFpTemp.push_back(*(yyvsp[-1].pFlowpipe));
		flowstar::ContinuousSystem system(*(yyvsp[-5].strVec), vecFpTemp);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = NONPOLY_TAYLOR;

		delete (yyvsp[-1].pFlowpipe);
	}

	delete (yyvsp[-5].strVec);
}
#line 3777 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 61:
#line 1787 "modelParser.y" /* yacc.c:1648  */
    {
	if(initialSets.size() > 0)
	{
		flowstar::ContinuousSystem system(dyn_A, dyn_B, dyn_ti, dyn_tv, initialSets);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = LTI;
	}
	else
	{
		std::vector<flowstar::Flowpipe> vecFpTemp;
		vecFpTemp.push_back(*(yyvsp[-1].pFlowpipe));
		flowstar::ContinuousSystem system(dyn_A, dyn_B, dyn_ti, dyn_tv, vecFpTemp);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = LTI;

		delete (yyvsp[-1].pFlowpipe);
	}
}
#line 3800 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 62:
#line 1807 "modelParser.y" /* yacc.c:1648  */
    {
	if(initialSets.size() > 0)
	{
		flowstar::ContinuousSystem system(dyn_A_t, dyn_B_t, dyn_ti_t, dyn_tv_t, initialSets);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = LTV;
	}
	else
	{
		std::vector<flowstar::Flowpipe> vecFpTemp;
		vecFpTemp.push_back(*(yyvsp[-1].pFlowpipe));
		flowstar::ContinuousSystem system(dyn_A_t, dyn_B_t, dyn_ti_t, dyn_tv_t, vecFpTemp);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = LTV;

		delete (yyvsp[-1].pFlowpipe);
	}
}
#line 3823 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 63:
#line 1827 "modelParser.y" /* yacc.c:1648  */
    {
	if(initialSets.size() > 0)
	{
		flowstar::ContinuousSystem system(*(yyvsp[-5].tmVec), initialSets);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = ONLY_PICARD_SYMB;
		continuousProblem.max_remainder_queue = (yyvsp[-8].dblVal);
	}
	else
	{
		std::vector<flowstar::Flowpipe> vecFpTemp;
		vecFpTemp.push_back(*(yyvsp[-1].pFlowpipe));
		flowstar::ContinuousSystem system(*(yyvsp[-5].tmVec), vecFpTemp);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = ONLY_PICARD_SYMB;
		continuousProblem.max_remainder_queue = (yyvsp[-8].dblVal);

		delete (yyvsp[-1].pFlowpipe);
	}

	delete (yyvsp[-5].tmVec);
}
#line 3850 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 64:
#line 1851 "modelParser.y" /* yacc.c:1648  */
    {
	if(initialSets.size() > 0)
	{
		flowstar::ContinuousSystem system(*(yyvsp[-5].strVec), initialSets);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = NONPOLY_TAYLOR_SYMB;
		continuousProblem.max_remainder_queue = (yyvsp[-8].dblVal);
	}
	else
	{
		std::vector<flowstar::Flowpipe> vecFpTemp;
		vecFpTemp.push_back(*(yyvsp[-1].pFlowpipe));
		flowstar::ContinuousSystem system(*(yyvsp[-5].strVec), vecFpTemp);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = NONPOLY_TAYLOR_SYMB;
		continuousProblem.max_remainder_queue = (yyvsp[-8].dblVal);

		delete (yyvsp[-1].pFlowpipe);
	}

	delete (yyvsp[-5].strVec);
}
#line 3877 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 65:
#line 1875 "modelParser.y" /* yacc.c:1648  */
    {
	if(initialSets.size() > 0)
	{
		flowstar::ContinuousSystem system(*(yyvsp[-5].tmVec), initialSets);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = ONLY_PICARD;
	}
	else
	{
		std::vector<flowstar::Flowpipe> vecFpTemp;
		vecFpTemp.push_back(*(yyvsp[-1].pFlowpipe));
		flowstar::ContinuousSystem system(*(yyvsp[-5].tmVec), vecFpTemp);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = ONLY_PICARD;

		delete (yyvsp[-1].pFlowpipe);
	}

	delete (yyvsp[-5].tmVec);
}
#line 3902 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 66:
#line 1897 "modelParser.y" /* yacc.c:1648  */
    {
	if(initialSets.size() > 0)
	{
		flowstar::ContinuousSystem system(*(yyvsp[-5].tmVec), initialSets);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = LOW_DEGREE;
	}
	else
	{
		std::vector<flowstar::Flowpipe> vecFpTemp;
		vecFpTemp.push_back(*(yyvsp[-1].pFlowpipe));
		flowstar::ContinuousSystem system(*(yyvsp[-5].tmVec), vecFpTemp);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = LOW_DEGREE;

		delete (yyvsp[-1].pFlowpipe);
	}

	delete (yyvsp[-5].tmVec);
}
#line 3927 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 67:
#line 1919 "modelParser.y" /* yacc.c:1648  */
    {
	if(initialSets.size() > 0)
	{
		flowstar::ContinuousSystem system(*(yyvsp[-5].tmVec), initialSets);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = HIGH_DEGREE;
	}
	else
	{
		std::vector<flowstar::Flowpipe> vecFpTemp;
		vecFpTemp.push_back(*(yyvsp[-1].pFlowpipe));
		flowstar::ContinuousSystem system(*(yyvsp[-5].tmVec), vecFpTemp);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = HIGH_DEGREE;

		delete (yyvsp[-1].pFlowpipe);
	}

	delete (yyvsp[-5].tmVec);
}
#line 3952 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 68:
#line 1941 "modelParser.y" /* yacc.c:1648  */
    {
	if(initialSets.size() > 0)
	{
		flowstar::ContinuousSystem system(*(yyvsp[-5].strVec), initialSets);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = NONPOLY_TAYLOR;
	}
	else
	{
		std::vector<flowstar::Flowpipe> vecFpTemp;
		vecFpTemp.push_back(*(yyvsp[-1].pFlowpipe));
		flowstar::ContinuousSystem system(*(yyvsp[-5].strVec), vecFpTemp);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = NONPOLY_TAYLOR;

		delete (yyvsp[-1].pFlowpipe);
	}

	delete (yyvsp[-5].strVec);
}
#line 3977 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 69:
#line 1963 "modelParser.y" /* yacc.c:1648  */
    {
	if(initialSets.size() > 0)
	{
		flowstar::ContinuousSystem system(dyn_A, dyn_B, dyn_ti, dyn_tv, initialSets);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = LTI;
	}
	else
	{
		std::vector<flowstar::Flowpipe> vecFpTemp;
		vecFpTemp.push_back(*(yyvsp[-1].pFlowpipe));
		flowstar::ContinuousSystem system(dyn_A, dyn_B, dyn_ti, dyn_tv, vecFpTemp);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = LTI;

		delete (yyvsp[-1].pFlowpipe);
	}
}
#line 4000 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 70:
#line 1983 "modelParser.y" /* yacc.c:1648  */
    {
	if(initialSets.size() > 0)
	{
		flowstar::ContinuousSystem system(dyn_A_t, dyn_B_t, dyn_ti_t, dyn_tv_t, initialSets);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = LTV;
	}
	else
	{
		std::vector<flowstar::Flowpipe> vecFpTemp;
		vecFpTemp.push_back(*(yyvsp[-1].pFlowpipe));
		flowstar::ContinuousSystem system(dyn_A_t, dyn_B_t, dyn_ti_t, dyn_tv_t, vecFpTemp);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = LTV;

		delete (yyvsp[-1].pFlowpipe);
	}
}
#line 4023 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 71:
#line 2003 "modelParser.y" /* yacc.c:1648  */
    {
	if(initialSets.size() > 0)
	{
		flowstar::ContinuousSystem system(*(yyvsp[-5].tmVec), initialSets);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = ONLY_PICARD_SYMB;
		continuousProblem.max_remainder_queue = (yyvsp[-8].dblVal);
	}
	else
	{
		std::vector<flowstar::Flowpipe> vecFpTemp;
		vecFpTemp.push_back(*(yyvsp[-1].pFlowpipe));
		flowstar::ContinuousSystem system(*(yyvsp[-5].tmVec), vecFpTemp);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = ONLY_PICARD_SYMB;
		continuousProblem.max_remainder_queue = (yyvsp[-8].dblVal);

		delete (yyvsp[-1].pFlowpipe);
	}

	delete (yyvsp[-5].tmVec);
}
#line 4050 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 72:
#line 2027 "modelParser.y" /* yacc.c:1648  */
    {
	if(initialSets.size() > 0)
	{
		flowstar::ContinuousSystem system(*(yyvsp[-5].strVec), initialSets);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = NONPOLY_TAYLOR_SYMB;
		continuousProblem.max_remainder_queue = (yyvsp[-8].dblVal);
	}
	else
	{
		std::vector<flowstar::Flowpipe> vecFpTemp;
		vecFpTemp.push_back(*(yyvsp[-1].pFlowpipe));
		flowstar::ContinuousSystem system(*(yyvsp[-5].strVec), vecFpTemp);
		continuousProblem.system = system;
		continuousProblem.integrationScheme = NONPOLY_TAYLOR_SYMB;
		continuousProblem.max_remainder_queue = (yyvsp[-8].dblVal);

		delete (yyvsp[-1].pFlowpipe);
	}

	delete (yyvsp[-5].strVec);
}
#line 4077 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 73:
#line 2052 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-14].dblVal) < 0)
	{
		parseError("The maximum jump depth should be a nonnegative integer.", lineNum);
		exit(1);
	}

	hybridProblem.maxJumps = (int)(yyvsp[-14].dblVal);
}
#line 4091 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 74:
#line 2063 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-14].dblVal) < 0)
	{
		parseError("The maximum jump depth should be a nonnegative integer.", lineNum);
		exit(1);
	}

	hybridProblem.maxJumps = (int)(yyvsp[-14].dblVal);
}
#line 4105 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 75:
#line 2075 "modelParser.y" /* yacc.c:1648  */
    {
	int id = hybridProblem.getIDForMode(*(yyvsp[-3].identifier));
	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "Mode %s has not been declared.", (*(yyvsp[-3].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	flowstar::Interval intZero;
	flowstar::Flowpipe initialSet(*(yyvsp[-1].intVec), intZero);
	hybridProblem.initialConfig(id, initialSet);

	int numVars = hybridProblem.stateVarNames.size();

	std::string tVar("local_t");
	hybridProblem.declareTMVar(tVar);
	continuousProblem.declareTMVar(tVar);

	char name[NAME_SIZE];

	for(int i=0; i<numVars; ++i)
	{
		sprintf(name, "%s%d", local_var_name, i+1);
		std::string tmVarName(name);
		hybridProblem.declareTMVar(tmVarName);
		continuousProblem.declareTMVar(tmVarName);
	}

	delete (yyvsp[-3].identifier);
	delete (yyvsp[-1].intVec);
}
#line 4143 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 76:
#line 2110 "modelParser.y" /* yacc.c:1648  */
    {
	int id = hybridProblem.getIDForMode(*(yyvsp[-5].identifier));
	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "Mode %s has not been declared.", (*(yyvsp[-5].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	flowstar::Flowpipe initialSet(*(yyvsp[-2].tmVec), *(yyvsp[-1].intVec));
	hybridProblem.initialConfig(id, initialSet);

	delete (yyvsp[-2].tmVec);
	delete (yyvsp[-1].intVec);
}
#line 4164 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 77:
#line 2129 "modelParser.y" /* yacc.c:1648  */
    {
	hybridProblem.declareMode(*(yyvsp[-11].identifier), *(yyvsp[-6].tmVec), *(yyvsp[-2].vecConstraints), ONLY_PICARD, mode_local_setting);
	mode_local_setting.clear();

	delete (yyvsp[-11].identifier);
	delete (yyvsp[-6].tmVec);
	delete (yyvsp[-2].vecConstraints);
}
#line 4177 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 78:
#line 2139 "modelParser.y" /* yacc.c:1648  */
    {
	hybridProblem.declareMode(*(yyvsp[-11].identifier), *(yyvsp[-6].tmVec), *(yyvsp[-2].vecConstraints), ONLY_PICARD, mode_local_setting);
	mode_local_setting.clear();

	delete (yyvsp[-11].identifier);
	delete (yyvsp[-6].tmVec);
	delete (yyvsp[-2].vecConstraints);
}
#line 4190 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 79:
#line 2149 "modelParser.y" /* yacc.c:1648  */
    {
	hybridProblem.declareMode(*(yyvsp[-11].identifier), *(yyvsp[-6].tmVec), *(yyvsp[-2].vecConstraints), LOW_DEGREE, mode_local_setting);
	mode_local_setting.clear();

	delete (yyvsp[-11].identifier);
	delete (yyvsp[-6].tmVec);
	delete (yyvsp[-2].vecConstraints);
}
#line 4203 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 80:
#line 2159 "modelParser.y" /* yacc.c:1648  */
    {
	hybridProblem.declareMode(*(yyvsp[-11].identifier), *(yyvsp[-6].tmVec), *(yyvsp[-2].vecConstraints), LOW_DEGREE, mode_local_setting);
	mode_local_setting.clear();

	delete (yyvsp[-11].identifier);
	delete (yyvsp[-6].tmVec);
	delete (yyvsp[-2].vecConstraints);
}
#line 4216 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 81:
#line 2169 "modelParser.y" /* yacc.c:1648  */
    {
	hybridProblem.declareMode(*(yyvsp[-11].identifier), *(yyvsp[-6].tmVec), *(yyvsp[-2].vecConstraints), HIGH_DEGREE, mode_local_setting);
	mode_local_setting.clear();

	delete (yyvsp[-11].identifier);
	delete (yyvsp[-6].tmVec);
	delete (yyvsp[-2].vecConstraints);
}
#line 4229 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 82:
#line 2179 "modelParser.y" /* yacc.c:1648  */
    {
	hybridProblem.declareMode(*(yyvsp[-11].identifier), *(yyvsp[-6].tmVec), *(yyvsp[-2].vecConstraints), HIGH_DEGREE, mode_local_setting);
	mode_local_setting.clear();

	delete (yyvsp[-11].identifier);
	delete (yyvsp[-6].tmVec);
	delete (yyvsp[-2].vecConstraints);
}
#line 4242 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 83:
#line 2189 "modelParser.y" /* yacc.c:1648  */
    {
	hybridProblem.declareMode(*(yyvsp[-11].identifier), *(yyvsp[-6].strVec), *(yyvsp[-2].vecConstraints), NONPOLY_TAYLOR, mode_local_setting);
	mode_local_setting.clear();

	delete (yyvsp[-11].identifier);
	delete (yyvsp[-6].strVec);
	delete (yyvsp[-2].vecConstraints);
}
#line 4255 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 84:
#line 2199 "modelParser.y" /* yacc.c:1648  */
    {
	hybridProblem.declareMode(*(yyvsp[-11].identifier), *(yyvsp[-6].strVec), *(yyvsp[-2].vecConstraints), NONPOLY_TAYLOR, mode_local_setting);
	mode_local_setting.clear();

	delete (yyvsp[-11].identifier);
	delete (yyvsp[-6].strVec);
	delete (yyvsp[-2].vecConstraints);
}
#line 4268 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 85:
#line 2209 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::LTI_Dynamics lti_dyn(dyn_A, dyn_B);
	hybridProblem.declareMode(*(yyvsp[-11].identifier), lti_dyn, *(yyvsp[-2].vecConstraints), mode_local_setting);
	mode_local_setting.clear();

	delete (yyvsp[-11].identifier);
	delete (yyvsp[-2].vecConstraints);
}
#line 4281 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 86:
#line 2219 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::LTI_Dynamics lti_dyn(dyn_A, dyn_B);
	hybridProblem.declareMode(*(yyvsp[-11].identifier), lti_dyn, *(yyvsp[-2].vecConstraints), mode_local_setting);
	mode_local_setting.clear();

	delete (yyvsp[-11].identifier);
	delete (yyvsp[-2].vecConstraints);
}
#line 4294 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 87:
#line 2229 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::LTV_Dynamics ltv_dyn(dyn_A_t, dyn_B_t);
	hybridProblem.declareMode(*(yyvsp[-11].identifier), ltv_dyn, *(yyvsp[-2].vecConstraints), mode_local_setting);
	mode_local_setting.clear();

	delete (yyvsp[-11].identifier);
	delete (yyvsp[-2].vecConstraints);
}
#line 4307 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 88:
#line 2239 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::LTV_Dynamics ltv_dyn(dyn_A_t, dyn_B_t);
	hybridProblem.declareMode(*(yyvsp[-11].identifier), ltv_dyn, *(yyvsp[-2].vecConstraints), mode_local_setting);
	mode_local_setting.clear();

	delete (yyvsp[-11].identifier);
	delete (yyvsp[-2].vecConstraints);
}
#line 4320 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 89:
#line 2252 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 4327 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 90:
#line 2255 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 4334 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 91:
#line 2260 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].dblVal) <= 0)
	{
		parseError("A time step-size should be larger than 0", lineNum);
		exit(1);
	}

	mode_local_setting.bAdaptiveSteps = false;
	mode_local_setting.step = (yyvsp[0].dblVal);
}
#line 4349 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 92:
#line 2272 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].dblVal) <= 0)
	{
		parseError("Remainder estimation should be a positive number.", lineNum);
		exit(1);
	}

	flowstar::Interval I(-(yyvsp[0].dblVal), (yyvsp[0].dblVal));

	for(int i=0; i<continuousProblem.stateVarNames.size(); ++i)
	{
		mode_local_setting.estimation.push_back(I);
	}
}
#line 4368 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 93:
#line 2288 "modelParser.y" /* yacc.c:1648  */
    {
	mode_local_setting.estimation = *(yyvsp[-1].intVec);
}
#line 4376 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 94:
#line 2293 "modelParser.y" /* yacc.c:1648  */
    {
	mode_local_setting.precondition = QR_PRE;
}
#line 4384 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 95:
#line 2298 "modelParser.y" /* yacc.c:1648  */
    {
	mode_local_setting.precondition = ID_PRE;
}
#line 4392 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 96:
#line 2303 "modelParser.y" /* yacc.c:1648  */
    {
	int order = (int)(yyvsp[0].dblVal);

	if(order <= 0)
	{
		parseError("Orders should be larger than zero.", lineNum);
		exit(1);
	}

	mode_local_setting.bAdaptiveOrders = false;
	mode_local_setting.orderType = UNIFORM;
	mode_local_setting.orders.push_back(order);
	mode_local_setting.globalMaxOrder = order;
}
#line 4411 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 97:
#line 2319 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].dblVal) <= 0)
	{
		parseError("The cutoff threshold should be a positive number.", lineNum);
		exit(1);
	}

	flowstar::Interval I(-(yyvsp[0].dblVal), (yyvsp[0].dblVal));
	mode_local_setting.cutoff_threshold = I;
}
#line 4426 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 98:
#line 2331 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-4].dblVal) <= 0 || (yyvsp[-1].dblVal) <= 0)
	{
		parseError("A time step-size should be larger than 0", lineNum);
		exit(1);
	}

	if((yyvsp[-4].dblVal) > (yyvsp[-1].dblVal))
	{
		parseError("MIN step should be no larger than MAX step.", lineNum);
		exit(1);
	}

	mode_local_setting.bAdaptiveSteps = true;
	mode_local_setting.step = (yyvsp[-1].dblVal);
	mode_local_setting.miniStep = (yyvsp[-4].dblVal);
	mode_local_setting.bAdaptiveOrders = false;
}
#line 4449 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 99:
#line 2351 "modelParser.y" /* yacc.c:1648  */
    {
	int minOrder = (int)(yyvsp[-4].dblVal);
	int maxOrder = (int)(yyvsp[-1].dblVal);

	if(minOrder <= 0 || maxOrder <= 0)
	{
		parseError("Orders should be larger than zero.", lineNum);
		exit(1);
	}

	if(minOrder > maxOrder)
	{
		parseError("MAX order should be no smaller than MIN order.", lineNum);
		exit(1);
	}

	mode_local_setting.bAdaptiveSteps = false;
	mode_local_setting.bAdaptiveOrders = true;
	mode_local_setting.orderType = UNIFORM;
	mode_local_setting.orders.push_back(minOrder);
	mode_local_setting.maxOrders.push_back(maxOrder);
	mode_local_setting.globalMaxOrder = maxOrder;
}
#line 4477 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 100:
#line 2376 "modelParser.y" /* yacc.c:1648  */
    {
	mode_local_setting.bAdaptiveOrders = false;
	mode_local_setting.orderType = MULTI;
	mode_local_setting.orders = *(yyvsp[-1].iVec);

	for(int i=0; i<(yyvsp[-1].iVec)->size(); ++i)
	{
		if((*(yyvsp[-1].iVec))[i] <= 0)
		{
			parseError("Orders should be larger than zero.", lineNum);
			exit(1);
		}
	}

	int maxOrder = (*(yyvsp[-1].iVec))[0];
	for(int i=1; i<(yyvsp[-1].iVec)->size(); ++i)
	{
		if(maxOrder < (*(yyvsp[-1].iVec))[i])
		{
			maxOrder = (*(yyvsp[-1].iVec))[i];
		}
	}

	mode_local_setting.globalMaxOrder = maxOrder;
}
#line 4507 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 101:
#line 2403 "modelParser.y" /* yacc.c:1648  */
    {
	mode_local_setting.bAdaptiveSteps = false;
	mode_local_setting.bAdaptiveOrders = true;
	mode_local_setting.orderType = MULTI;
	mode_local_setting.orders = *(yyvsp[-7].iVec);
	mode_local_setting.maxOrders = *(yyvsp[-2].iVec);

	if((yyvsp[-7].iVec)->size() != (yyvsp[-2].iVec)->size())
	{
		parseError("Orders are not properly specified.", lineNum);
		exit(1);
	}

	for(int i=0; i<(yyvsp[-2].iVec)->size(); ++i)
	{
		if((*(yyvsp[-7].iVec))[i] <= 0 || (*(yyvsp[-2].iVec))[i] <= 0)
		{
			parseError("Orders should be larger than zero.", lineNum);
			exit(1);
		}

		if((*(yyvsp[-7].iVec))[i] > (*(yyvsp[-2].iVec))[i])
		{
			parseError("MAX order should be no smaller than MIN order.", lineNum);
			exit(1);
		}
	}

	int maxOrder = (*(yyvsp[-2].iVec))[0];
	for(int i=1; i<(yyvsp[-2].iVec)->size(); ++i)
	{
		if(maxOrder < (*(yyvsp[-2].iVec))[i])
		{
			maxOrder = (*(yyvsp[-2].iVec))[i];
		}
	}

	mode_local_setting.globalMaxOrder = maxOrder;
}
#line 4551 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 102:
#line 2443 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 4558 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 103:
#line 2448 "modelParser.y" /* yacc.c:1648  */
    {
	int startID = hybridProblem.getIDForMode(*(yyvsp[-15].identifier));
	if(startID < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "Mode %s has not been declared.", (*(yyvsp[-15].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	int endID = hybridProblem.getIDForMode(*(yyvsp[-12].identifier));
	if(endID < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "Mode %s has not been declared.", (*(yyvsp[-12].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	if((yyvsp[-1].dVecVec)->size() > 0)
	{
		hybridProblem.declareTrans(startID, endID, *(yyvsp[-9].vecConstraints), *(yyvsp[-5].resetMap), PARA_AGGREG, *(yyvsp[-1].dVecVec));
	}
	else
	{
		std::vector<std::vector<double> > emptyVec;
		hybridProblem.declareTrans(startID, endID, *(yyvsp[-9].vecConstraints), *(yyvsp[-5].resetMap), PARA_AGGREG, emptyVec);
	}
}
#line 4592 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 104:
#line 2479 "modelParser.y" /* yacc.c:1648  */
    {
	int startID = hybridProblem.getIDForMode(*(yyvsp[-12].identifier));
	if(startID < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "Mode %s has not been declared.", (*(yyvsp[-12].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	int endID = hybridProblem.getIDForMode(*(yyvsp[-9].identifier));
	if(endID < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "Mode %s has not been declared.", (*(yyvsp[-9].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	std::vector<std::vector<double> > empty;
	hybridProblem.declareTrans(startID, endID, *(yyvsp[-6].vecConstraints), *(yyvsp[-2].resetMap), INTERVAL_AGGREG, empty);
}
#line 4619 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 105:
#line 2502 "modelParser.y" /* yacc.c:1648  */
    {
	hybridProblem.declareTrans();
}
#line 4627 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 106:
#line 2508 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.resetMap) = (yyvsp[-10].resetMap);

	int id = hybridProblem.getIDForStateVar(*(yyvsp[-9].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-9].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	if((yyvsp[-3].dblVal) > (yyvsp[-1].dblVal))
	{
		parseError("Invalid remainder interval.", lineNum);
		exit(1);
	}

	flowstar::Interval I((yyvsp[-3].dblVal), (yyvsp[-1].dblVal));
	flowstar::TaylorModel tmTemp(*(yyvsp[-6].poly), I);
	(yyval.resetMap)->tmvReset.tms[id] = tmTemp;

	delete (yyvsp[-6].poly);
}
#line 4657 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 107:
#line 2535 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.resetMap) = (yyvsp[-4].resetMap);

	int id = hybridProblem.getIDForStateVar(*(yyvsp[-3].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-3].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	flowstar::Interval intZero;
	flowstar::TaylorModel tmTemp(*(yyvsp[0].poly), intZero);
	(yyval.resetMap)->tmvReset.tms[id] = tmTemp;

	delete (yyvsp[0].poly);
}
#line 4681 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 108:
#line 2555 "modelParser.y" /* yacc.c:1648  */
    {
	int numVars = hybridProblem.stateVarNames.size();

	flowstar::Matrix coefficients_identity_reset(numVars, numVars+1);

	for(int i=0; i<numVars; ++i)
	{
		coefficients_identity_reset.set(1, i, i+1);
	}

	flowstar::TaylorModelVec tmvReset(coefficients_identity_reset);

	(yyval.resetMap) = new flowstar::ResetMap(tmvReset);
}
#line 4700 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 109:
#line 2572 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.dVecVec)->push_back(*(yyvsp[0].dVec));
	delete (yyvsp[0].dVec);
}
#line 4709 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 110:
#line 2577 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.dVecVec) = new std::vector<std::vector<double> >(0);
}
#line 4717 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 111:
#line 2583 "modelParser.y" /* yacc.c:1648  */
    {
	int rangeDim = (yyvsp[-1].dVec)->size();

	if(rangeDim != hybridProblem.stateVarNames.size())
	{
		parseError("The vector dimension should be equivalent to the system dimension.", lineNum);
		exit(1);
	}

	(yyval.dVec) = new std::vector<double>(0);

	for(int i=0; i<rangeDim; ++i)
	{
		(yyval.dVec)->push_back(0);
	}

	bool bZero = true;
	for(int i=0; i<rangeDim; ++i)
	{
		if((*(yyvsp[-1].dVec))[i] < -THRESHOLD_LOW || (*(yyvsp[-1].dVec))[i] > THRESHOLD_LOW)
		{
			if(bZero)
			{
				bZero = false;
			}
		}

		(*(yyval.dVec))[i] = (*(yyvsp[-1].dVec))[i];
	}

	if(bZero)
	{
		parseError("A template vector should not be zero.", lineNum);
		exit(1);
	}

	delete (yyvsp[-1].dVec);
}
#line 4760 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 112:
#line 2624 "modelParser.y" /* yacc.c:1648  */
    {
	int id = hybridProblem.getIDForStateVar(*(yyvsp[-2].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-2].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	(yyval.dVec) = (yyvsp[-4].dVec);
	(*(yyval.dVec))[id] = (yyvsp[0].dblVal);
	delete (yyvsp[-2].identifier);
}
#line 4780 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 113:
#line 2641 "modelParser.y" /* yacc.c:1648  */
    {
	int num = hybridProblem.stateVarNames.size();
	(yyval.dVec) = new std::vector<double>(num);

	int id = hybridProblem.getIDForStateVar(*(yyvsp[-2].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-2].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	(*(yyval.dVec))[id] = (yyvsp[0].dblVal);
	delete (yyvsp[-2].identifier);
}
#line 4802 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 114:
#line 2661 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 4809 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 115:
#line 2666 "modelParser.y" /* yacc.c:1648  */
    {
	if(!continuousProblem.declareStateVar(*(yyvsp[0].identifier)))
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s has already been declared.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	hybridProblem.declareStateVar(*(yyvsp[0].identifier));
	delete (yyvsp[0].identifier);
}
#line 4826 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 116:
#line 2680 "modelParser.y" /* yacc.c:1648  */
    {
	if(!continuousProblem.declareStateVar(*(yyvsp[0].identifier)))
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s has already been declared.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	hybridProblem.declareStateVar(*(yyvsp[0].identifier));
	delete (yyvsp[0].identifier);
}
#line 4843 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 117:
#line 2697 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 4850 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 118:
#line 2702 "modelParser.y" /* yacc.c:1648  */
    {
	if(continuousProblem.getIDForStateVar(*(yyvsp[-2].identifier)) != -1)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "%s has already been declared as a state variable.", (*(yyvsp[-2].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}
	else
	{
		flowstar::Interval range((yyvsp[0].dblVal));

		if(!continuousProblem.declarePar(*(yyvsp[-2].identifier), range))
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "Parameter %s has already been declared.", (*(yyvsp[-2].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}

		hybridProblem.declarePar(*(yyvsp[-2].identifier), range);
	}
}
#line 4878 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 119:
#line 2727 "modelParser.y" /* yacc.c:1648  */
    {
	if(continuousProblem.getIDForStateVar(*(yyvsp[-2].identifier)) != -1)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "%s has already been declared as a state variable.", (*(yyvsp[-2].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}
	else
	{
		flowstar::Interval range((yyvsp[0].dblVal));

		if(!continuousProblem.declarePar(*(yyvsp[-2].identifier), range))
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "Parameter %s has already been declared.", (*(yyvsp[-2].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}

		hybridProblem.declarePar(*(yyvsp[-2].identifier), range);
	}
}
#line 4906 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 120:
#line 2754 "modelParser.y" /* yacc.c:1648  */
    {
	if(continuousProblem.getIDForStateVar(*(yyvsp[0].identifier)) != -1)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "%s has already been declared as a state variable.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}
	else
	{
		if(continuousProblem.getIDForPar(*(yyvsp[0].identifier)) != -1)
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "%s has already been declared as a parameter.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
		else
		{
			if(!continuousProblem.declareTIPar(*(yyvsp[0].identifier)))
			{
				char errMsg[MSG_SIZE];
				sprintf(errMsg, "Time-invariant uncertainty %s has already been declared.", (*(yyvsp[0].identifier)).c_str());
				parseError(errMsg, lineNum);
				exit(1);
			}
		}
	}
}
#line 4940 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 121:
#line 2785 "modelParser.y" /* yacc.c:1648  */
    {
	if(continuousProblem.getIDForStateVar(*(yyvsp[0].identifier)) != -1)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "%s has already been declared as a state variable.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}
	else
	{
		if(continuousProblem.getIDForPar(*(yyvsp[0].identifier)) != -1)
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "%s has already been declared as a parameter.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
		else
		{
			if(!continuousProblem.declareTIPar(*(yyvsp[0].identifier)))
			{
				char errMsg[MSG_SIZE];
				sprintf(errMsg, "Uncertainty %s has already been declared.", (*(yyvsp[0].identifier)).c_str());
				parseError(errMsg, lineNum);
				exit(1);
			}
		}
	}
}
#line 4974 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 122:
#line 2815 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 4981 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 123:
#line 2821 "modelParser.y" /* yacc.c:1648  */
    {
	if(continuousProblem.getIDForStateVar(*(yyvsp[0].identifier)) != -1)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "%s has already been declared as a state variable.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}
	else
	{
		if(continuousProblem.getIDForPar(*(yyvsp[0].identifier)) != -1)
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "%s has already been declared as a parameter.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
		else
		{
			if(!continuousProblem.declareTVPar(*(yyvsp[0].identifier)))
			{
				char errMsg[MSG_SIZE];
				sprintf(errMsg, "Uncertainty %s has already been declared.", (*(yyvsp[0].identifier)).c_str());
				parseError(errMsg, lineNum);
				exit(1);
			}
		}

//		hybridProblem.declareUnc(*$2, range);
	}
}
#line 5017 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 124:
#line 2854 "modelParser.y" /* yacc.c:1648  */
    {
	if(continuousProblem.getIDForStateVar(*(yyvsp[0].identifier)) != -1)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "%s has already been declared as a state variable.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}
	else
	{
		if(continuousProblem.getIDForPar(*(yyvsp[0].identifier)) != -1)
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "%s has already been declared as a parameter.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
		else
		{
			if(!continuousProblem.declareTVPar(*(yyvsp[0].identifier)))
			{
				char errMsg[MSG_SIZE];
				sprintf(errMsg, "Uncertainty %s has already been declared.", (*(yyvsp[0].identifier)).c_str());
				parseError(errMsg, lineNum);
				exit(1);
			}
		}

//		hybridProblem.declareUnc(*$1, range);
	}
}
#line 5053 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 125:
#line 2886 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 5060 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 126:
#line 2891 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-12].dblVal) <= 0)
	{
		parseError("A time step-size should be larger than 0", lineNum);
		exit(1);
	}

	int order = (int)(yyvsp[-5].dblVal);

	if(order <= 0)
	{
		parseError("Orders should be larger than zero.", lineNum);
		exit(1);
	}

	continuousProblem.bAdaptiveSteps = false;
	continuousProblem.step = (yyvsp[-12].dblVal);
	continuousProblem.time = (yyvsp[-10].dblVal);
	continuousProblem.bAdaptiveOrders = false;
	continuousProblem.orderType = UNIFORM;
	continuousProblem.orders.push_back(order);
	continuousProblem.globalMaxOrder = order;

	hybridProblem.global_setting.bAdaptiveSteps = false;
	hybridProblem.global_setting.step = (yyvsp[-12].dblVal);
	hybridProblem.time = (yyvsp[-10].dblVal);
	hybridProblem.global_setting.bAdaptiveOrders = false;
	hybridProblem.global_setting.orderType = UNIFORM;
	hybridProblem.global_setting.orders.push_back(order);
	hybridProblem.global_setting.globalMaxOrder = order;

	if((yyvsp[-3].dblVal) <= 0)
	{
		parseError("The cutoff threshold should be a positive number.", lineNum);
		exit(1);
	}

	flowstar::Interval cutoff_threshold(-(yyvsp[-3].dblVal),(yyvsp[-3].dblVal));
	continuousProblem.cutoff_threshold = cutoff_threshold;
	hybridProblem.global_setting.cutoff_threshold = cutoff_threshold;

	intervalNumPrecision = (int)(yyvsp[-1].dblVal);
}
#line 5108 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 127:
#line 2936 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-18].dblVal) <= 0)
	{
		parseError("A time step-size should be larger than 0", lineNum);
		exit(1);
	}

	int minOrder = (int)(yyvsp[-9].dblVal);
	int maxOrder = (int)(yyvsp[-6].dblVal);

	if(minOrder <= 0 || maxOrder <= 0)
	{
		parseError("Orders should be larger than zero.", lineNum);
		exit(1);
	}

	if(minOrder > maxOrder)
	{
		parseError("MAX order should be no smaller than MIN order.", lineNum);
		exit(1);
	}

	continuousProblem.bAdaptiveSteps = false;
	continuousProblem.step = (yyvsp[-18].dblVal);
	continuousProblem.time = (yyvsp[-16].dblVal);
	continuousProblem.bAdaptiveOrders = true;
	continuousProblem.orderType = UNIFORM;
	continuousProblem.orders.push_back(minOrder);
	continuousProblem.maxOrders.push_back(maxOrder);
	continuousProblem.globalMaxOrder = maxOrder;

	hybridProblem.global_setting.bAdaptiveSteps = false;
	hybridProblem.global_setting.step = (yyvsp[-18].dblVal);
	hybridProblem.time = (yyvsp[-16].dblVal);
	hybridProblem.global_setting.bAdaptiveOrders = true;
	hybridProblem.global_setting.orderType = UNIFORM;
	hybridProblem.global_setting.orders.push_back(minOrder);
	hybridProblem.global_setting.maxOrders.push_back(maxOrder);
	hybridProblem.global_setting.globalMaxOrder = maxOrder;

	if((yyvsp[-3].dblVal) <= 0)
	{
		parseError("The cutoff threshold should be a positive number.", lineNum);
		exit(1);
	}

	flowstar::Interval cutoff_threshold(-(yyvsp[-3].dblVal),(yyvsp[-3].dblVal));
	continuousProblem.cutoff_threshold = cutoff_threshold;
	hybridProblem.global_setting.cutoff_threshold = cutoff_threshold;

	intervalNumPrecision = (int)(yyvsp[-1].dblVal);
}
#line 5165 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 128:
#line 2990 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-14].dblVal) <= 0)
	{
		parseError("A time step-size should be larger than 0", lineNum);
		exit(1);
	}

	continuousProblem.bAdaptiveSteps = false;
	continuousProblem.step = (yyvsp[-14].dblVal);
	continuousProblem.time = (yyvsp[-12].dblVal);
	continuousProblem.bAdaptiveOrders = false;
	continuousProblem.orderType = MULTI;
	continuousProblem.orders = *(yyvsp[-6].iVec);

	hybridProblem.global_setting.bAdaptiveSteps = false;
	hybridProblem.global_setting.step = (yyvsp[-14].dblVal);
	hybridProblem.time = (yyvsp[-12].dblVal);
	hybridProblem.global_setting.bAdaptiveOrders = false;
	hybridProblem.global_setting.orderType = MULTI;
	hybridProblem.global_setting.orders = *(yyvsp[-6].iVec);

	for(int i=0; i<(yyvsp[-6].iVec)->size(); ++i)
	{
		if((*(yyvsp[-6].iVec))[i] <= 0)
		{
			parseError("Orders should be larger than zero.", lineNum);
			exit(1);
		}
	}

	int maxOrder = (*(yyvsp[-6].iVec))[0];
	for(int i=1; i<(yyvsp[-6].iVec)->size(); ++i)
	{
		if(maxOrder < (*(yyvsp[-6].iVec))[i])
		{
			maxOrder = (*(yyvsp[-6].iVec))[i];
		}
	}

	continuousProblem.globalMaxOrder = maxOrder;
	hybridProblem.global_setting.globalMaxOrder = maxOrder;

	if((yyvsp[-3].dblVal) <= 0)
	{
		parseError("The cutoff threshold should be a positive number.", lineNum);
		exit(1);
	}

	flowstar::Interval cutoff_threshold(-(yyvsp[-3].dblVal),(yyvsp[-3].dblVal));
	continuousProblem.cutoff_threshold = cutoff_threshold;
	hybridProblem.global_setting.cutoff_threshold = cutoff_threshold;

	intervalNumPrecision = (int)(yyvsp[-1].dblVal);

	delete (yyvsp[-6].iVec);
}
#line 5226 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 129:
#line 3048 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-22].dblVal) <= 0)
	{
		parseError("A time step-size should be larger than 0", lineNum);
		exit(1);
	}

	continuousProblem.bAdaptiveSteps = false;
	continuousProblem.step = (yyvsp[-22].dblVal);
	continuousProblem.time = (yyvsp[-20].dblVal);
	continuousProblem.bAdaptiveOrders = true;
	continuousProblem.orderType = MULTI;
	continuousProblem.orders = *(yyvsp[-12].iVec);
	continuousProblem.maxOrders = *(yyvsp[-7].iVec);

	hybridProblem.global_setting.bAdaptiveSteps = false;
	hybridProblem.global_setting.step = (yyvsp[-22].dblVal);
	hybridProblem.time = (yyvsp[-20].dblVal);
	hybridProblem.global_setting.bAdaptiveOrders = true;
	hybridProblem.global_setting.orderType = MULTI;
	hybridProblem.global_setting.orders = *(yyvsp[-12].iVec);
	hybridProblem.global_setting.maxOrders = *(yyvsp[-7].iVec);

	if((yyvsp[-12].iVec)->size() != (yyvsp[-7].iVec)->size())
	{
		parseError("Orders are not properly specified.", lineNum);
		exit(1);
	}

	for(int i=0; i<(yyvsp[-7].iVec)->size(); ++i)
	{
		if((*(yyvsp[-12].iVec))[i] <= 0 || (*(yyvsp[-7].iVec))[i] <= 0)
		{
			parseError("Orders should be larger than zero.", lineNum);
			exit(1);
		}

		if((*(yyvsp[-12].iVec))[i] > (*(yyvsp[-7].iVec))[i])
		{
			parseError("MAX order should be no smaller than MIN order.", lineNum);
			exit(1);
		}
	}

	int maxOrder = (*(yyvsp[-7].iVec))[0];
	for(int i=1; i<(yyvsp[-7].iVec)->size(); ++i)
	{
		if(maxOrder < (*(yyvsp[-7].iVec))[i])
		{
			maxOrder = (*(yyvsp[-7].iVec))[i];
		}
	}

	continuousProblem.globalMaxOrder = maxOrder;
	hybridProblem.global_setting.globalMaxOrder = maxOrder;

	if((yyvsp[-3].dblVal) <= 0)
	{
		parseError("The cutoff threshold should be a positive number.", lineNum);
		exit(1);
	}

	flowstar::Interval cutoff_threshold(-(yyvsp[-3].dblVal),(yyvsp[-3].dblVal));
	continuousProblem.cutoff_threshold = cutoff_threshold;
	hybridProblem.global_setting.cutoff_threshold = cutoff_threshold;

	intervalNumPrecision = (int)(yyvsp[-1].dblVal);

	delete (yyvsp[-12].iVec);
	delete (yyvsp[-7].iVec);
}
#line 5302 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 130:
#line 3121 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-16].dblVal) <= 0 || (yyvsp[-13].dblVal) <= 0)
	{
		parseError("A time step-size should be larger than 0", lineNum);
		exit(1);
	}

	if((yyvsp[-16].dblVal) > (yyvsp[-13].dblVal))
	{
		parseError("MIN step should be no larger than MAX step.", lineNum);
		exit(1);
	}

	int order = (int)(yyvsp[-5].dblVal);

	if(order <= 0)
	{
		parseError("Orders should be larger than zero.", lineNum);
		exit(1);
	}

	continuousProblem.bAdaptiveSteps = true;
	continuousProblem.step = (yyvsp[-13].dblVal);
	continuousProblem.miniStep = (yyvsp[-16].dblVal);
	continuousProblem.time = (yyvsp[-10].dblVal);
	continuousProblem.bAdaptiveOrders = false;
	continuousProblem.orderType = UNIFORM;
	continuousProblem.orders.push_back(order);
	continuousProblem.globalMaxOrder = order;

	hybridProblem.global_setting.bAdaptiveSteps = true;
	hybridProblem.global_setting.step = (yyvsp[-13].dblVal);
	hybridProblem.global_setting.miniStep = (yyvsp[-16].dblVal);
	hybridProblem.time = (yyvsp[-10].dblVal);
	hybridProblem.global_setting.bAdaptiveOrders = false;
	hybridProblem.global_setting.orderType = UNIFORM;
	hybridProblem.global_setting.orders.push_back(order);
	hybridProblem.global_setting.globalMaxOrder = order;

	if((yyvsp[-3].dblVal) <= 0)
	{
		parseError("The cutoff threshold should be a positive number.", lineNum);
		exit(1);
	}

	flowstar::Interval cutoff_threshold(-(yyvsp[-3].dblVal),(yyvsp[-3].dblVal));
	continuousProblem.cutoff_threshold = cutoff_threshold;
	hybridProblem.global_setting.cutoff_threshold = cutoff_threshold;

	intervalNumPrecision = (int)(yyvsp[-1].dblVal);
}
#line 5358 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 131:
#line 3174 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[-18].dblVal) <= 0 || (yyvsp[-15].dblVal) <= 0)
	{
		parseError("A time step-size should be larger than 0", lineNum);
		exit(1);
	}

	if((yyvsp[-18].dblVal) > (yyvsp[-15].dblVal))
	{
		parseError("MIN step should be no larger than MAX step.", lineNum);
		exit(1);
	}

	for(int i=0; i<(yyvsp[-6].iVec)->size(); ++i)
	{
		if((*(yyvsp[-6].iVec))[i] <= 0)
		{
			parseError("Orders should be larger than zero.", lineNum);
			exit(1);
		}
	}

	continuousProblem.bAdaptiveSteps = true;
	continuousProblem.step = (yyvsp[-15].dblVal);
	continuousProblem.miniStep = (yyvsp[-18].dblVal);
	continuousProblem.time = (yyvsp[-12].dblVal);
	continuousProblem.bAdaptiveOrders = false;
	continuousProblem.orderType = MULTI;
	continuousProblem.orders = *(yyvsp[-6].iVec);

	hybridProblem.global_setting.bAdaptiveSteps = true;
	hybridProblem.global_setting.step = (yyvsp[-15].dblVal);
	hybridProblem.global_setting.miniStep = (yyvsp[-18].dblVal);
	hybridProblem.time = (yyvsp[-12].dblVal);
	hybridProblem.global_setting.bAdaptiveOrders = false;
	hybridProblem.global_setting.orderType = MULTI;
	hybridProblem.global_setting.orders = *(yyvsp[-6].iVec);

	int maxOrder = (*(yyvsp[-6].iVec))[0];
	for(int i=1; i<(yyvsp[-6].iVec)->size(); ++i)
	{
		if(maxOrder < (*(yyvsp[-6].iVec))[i])
		{
			maxOrder = (*(yyvsp[-6].iVec))[i];
		}
	}

	continuousProblem.globalMaxOrder = maxOrder;
	hybridProblem.global_setting.globalMaxOrder = maxOrder;

	if((yyvsp[-3].dblVal) <= 0)
	{
		parseError("The cutoff threshold should be a positive number.", lineNum);
		exit(1);
	}

	flowstar::Interval cutoff_threshold(-(yyvsp[-3].dblVal),(yyvsp[-3].dblVal));
	continuousProblem.cutoff_threshold = cutoff_threshold;
	hybridProblem.global_setting.cutoff_threshold = cutoff_threshold;

	intervalNumPrecision = (int)(yyvsp[-1].dblVal);

	delete (yyvsp[-6].iVec);
}
#line 5427 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 132:
#line 3241 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].dblVal) <= 0)
	{
		parseError("Remainder estimation should be a positive number.", lineNum);
		exit(1);
	}

	flowstar::Interval I(-(yyvsp[0].dblVal), (yyvsp[0].dblVal));

	for(int i=0; i<continuousProblem.stateVarNames.size(); ++i)
	{
		continuousProblem.estimation.push_back(I);
		hybridProblem.global_setting.estimation.push_back(I);
	}
}
#line 5447 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 133:
#line 3258 "modelParser.y" /* yacc.c:1648  */
    {
	for(int i=0; i<(yyvsp[-1].intVec)->size(); ++i)
	{
		if((*(yyvsp[-1].intVec))[i].inf() >= (*(yyvsp[-1].intVec))[i].sup() - THRESHOLD_LOW)
		{
			parseError("Invalid remainder estimation.", lineNum);
			exit(1);
		}
	}

	continuousProblem.estimation = *(yyvsp[-1].intVec);
	hybridProblem.global_setting.estimation = *(yyvsp[-1].intVec);
	delete (yyvsp[-1].intVec);
}
#line 5466 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 134:
#line 3275 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.intVec) = (yyvsp[-8].intVec);
	int id = continuousProblem.getIDForStateVar(*(yyvsp[-6].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-6].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	if((yyvsp[-3].dblVal) >= (yyvsp[-1].dblVal))
	{
		parseError("Invalid remainder estimation.", lineNum);
		exit(1);
	}

	flowstar::Interval I((yyvsp[-3].dblVal),(yyvsp[-1].dblVal));
	(*(yyval.intVec))[id] = I;
	delete (yyvsp[-6].identifier);
}
#line 5493 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 135:
#line 3299 "modelParser.y" /* yacc.c:1648  */
    {
	int numVars = continuousProblem.stateVarNames.size();
	(yyval.intVec) = new std::vector<flowstar::Interval>(numVars);

	int id = continuousProblem.getIDForStateVar(*(yyvsp[-6].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-6].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	if((yyvsp[-3].dblVal) >= (yyvsp[-1].dblVal))
	{
		parseError("Invalid remainder estimation.", lineNum);
		exit(1);
	}

	flowstar::Interval I((yyvsp[-3].dblVal),(yyvsp[-1].dblVal));
	(*(yyval.intVec))[id] = I;
	delete (yyvsp[-6].identifier);
}
#line 5522 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 136:
#line 3326 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.iVec) = (yyvsp[-4].iVec);
	int id = continuousProblem.getIDForStateVar(*(yyvsp[-2].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-2].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	(*(yyval.iVec))[id] = (int)(yyvsp[0].dblVal);
	delete (yyvsp[-2].identifier);
}
#line 5542 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 137:
#line 3343 "modelParser.y" /* yacc.c:1648  */
    {
	int numVars = continuousProblem.stateVarNames.size();
	(yyval.iVec) = new std::vector<int>(numVars);
	for(int i=0; i<numVars; ++i)
	{
		(*(yyval.iVec))[i] = 0;
	}

	int id = continuousProblem.getIDForStateVar(*(yyvsp[-2].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-2].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	(*(yyval.iVec))[id] = (int)(yyvsp[0].dblVal);
	delete (yyvsp[-2].identifier);
}
#line 5568 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 138:
#line 3367 "modelParser.y" /* yacc.c:1648  */
    {
	continuousProblem.precondition = QR_PRE;
	hybridProblem.global_setting.precondition = QR_PRE;
}
#line 5577 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 139:
#line 3373 "modelParser.y" /* yacc.c:1648  */
    {
	continuousProblem.precondition = ID_PRE;
	hybridProblem.global_setting.precondition = ID_PRE;
}
#line 5586 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 140:
#line 3380 "modelParser.y" /* yacc.c:1648  */
    {
	int x = continuousProblem.getIDForStateVar(*(yyvsp[-2].identifier));
	int y = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));
	std::string tVar("t");

	if(x < 0)
	{
		if((yyvsp[-2].identifier)->compare(tVar) == 0)
		{
			x = -1;
		}
		else
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-2].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
	}

	if(y < 0)
	{
		if((yyvsp[0].identifier)->compare(tVar) == 0)
		{
			y = -1;
		}
		else
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
	}

	continuousProblem.outputAxes.push_back(x);
	continuousProblem.outputAxes.push_back(y);
	continuousProblem.plotSetting = PLOT_INTERVAL;
	continuousProblem.plotFormat = PLOT_GNUPLOT;

	hybridProblem.outputAxes.push_back(x);
	hybridProblem.outputAxes.push_back(y);
	hybridProblem.plotSetting = PLOT_INTERVAL;
	hybridProblem.plotFormat = PLOT_GNUPLOT;

	delete (yyvsp[-2].identifier);
	delete (yyvsp[0].identifier);
}
#line 5639 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 141:
#line 3430 "modelParser.y" /* yacc.c:1648  */
    {
	int x = continuousProblem.getIDForStateVar(*(yyvsp[-2].identifier));
	int y = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));
	std::string tVar("t");

	if(x < 0)
	{
		if((yyvsp[-2].identifier)->compare(tVar) == 0)
		{
			x = -1;
		}
		else
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "State Variable %s is not declared.", (*(yyvsp[-2].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
	}

	if(y < 0)
	{
		if((yyvsp[0].identifier)->compare(tVar) == 0)
		{
			y = -1;
		}
		else
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
	}

	continuousProblem.outputAxes.push_back(x);
	continuousProblem.outputAxes.push_back(y);
	continuousProblem.plotSetting = PLOT_OCTAGON;
	continuousProblem.plotFormat = PLOT_GNUPLOT;

	hybridProblem.outputAxes.push_back(x);
	hybridProblem.outputAxes.push_back(y);
	hybridProblem.plotSetting = PLOT_OCTAGON;
	hybridProblem.plotFormat = PLOT_GNUPLOT;

	delete (yyvsp[-2].identifier);
	delete (yyvsp[0].identifier);
}
#line 5692 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 142:
#line 3480 "modelParser.y" /* yacc.c:1648  */
    {
	int x = continuousProblem.getIDForStateVar(*(yyvsp[-2].identifier));
	int y = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));
	std::string tVar("t");

	if(x < 0)
	{
		if((yyvsp[-2].identifier)->compare(tVar) == 0)
		{
			x = -1;
		}
		else
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-2].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
	}

	if(y < 0)
	{
		if((yyvsp[0].identifier)->compare(tVar) == 0)
		{
			y = -1;
		}
		else
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
	}

	continuousProblem.outputAxes.push_back(x);
	continuousProblem.outputAxes.push_back(y);
	continuousProblem.plotSetting = PLOT_GRID;
	continuousProblem.numSections = (int)(yyvsp[-3].dblVal);
	continuousProblem.plotFormat = PLOT_GNUPLOT;

	hybridProblem.outputAxes.push_back(x);
	hybridProblem.outputAxes.push_back(y);
	hybridProblem.plotSetting = PLOT_GRID;
	hybridProblem.numSections = (int)(yyvsp[-3].dblVal);
	hybridProblem.plotFormat = PLOT_GNUPLOT;

	delete (yyvsp[-2].identifier);
	delete (yyvsp[0].identifier);
}
#line 5747 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 143:
#line 3532 "modelParser.y" /* yacc.c:1648  */
    {
	int x = continuousProblem.getIDForStateVar(*(yyvsp[-2].identifier));
	int y = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));
	std::string tVar("t");

	if(x < 0)
	{
		if((yyvsp[-2].identifier)->compare(tVar) == 0)
		{
			x = -1;
		}
		else
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-2].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
	}

	if(y < 0)
	{
		if((yyvsp[0].identifier)->compare(tVar) == 0)
		{
			y = -1;
		}
		else
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
	}

	continuousProblem.outputAxes.push_back(x);
	continuousProblem.outputAxes.push_back(y);
	continuousProblem.plotSetting = PLOT_INTERVAL;
	continuousProblem.plotFormat = PLOT_MATLAB;

	hybridProblem.outputAxes.push_back(x);
	hybridProblem.outputAxes.push_back(y);
	hybridProblem.plotSetting = PLOT_INTERVAL;
	hybridProblem.plotFormat = PLOT_MATLAB;

	delete (yyvsp[-2].identifier);
	delete (yyvsp[0].identifier);
}
#line 5800 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 144:
#line 3582 "modelParser.y" /* yacc.c:1648  */
    {
	int x = continuousProblem.getIDForStateVar(*(yyvsp[-2].identifier));
	int y = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));
	std::string tVar("t");

	if(x < 0)
	{
		if((yyvsp[-2].identifier)->compare(tVar) == 0)
		{
			x = -1;
		}
		else
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "State Variable %s is not declared.", (*(yyvsp[-2].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
	}

	if(y < 0)
	{
		if((yyvsp[0].identifier)->compare(tVar) == 0)
		{
			y = -1;
		}
		else
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
	}

	continuousProblem.outputAxes.push_back(x);
	continuousProblem.outputAxes.push_back(y);
	continuousProblem.plotSetting = PLOT_OCTAGON;
	continuousProblem.plotFormat = PLOT_MATLAB;

	hybridProblem.outputAxes.push_back(x);
	hybridProblem.outputAxes.push_back(y);
	hybridProblem.plotSetting = PLOT_OCTAGON;
	hybridProblem.plotFormat = PLOT_MATLAB;

	delete (yyvsp[-2].identifier);
	delete (yyvsp[0].identifier);
}
#line 5853 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 145:
#line 3632 "modelParser.y" /* yacc.c:1648  */
    {
	int x = continuousProblem.getIDForStateVar(*(yyvsp[-2].identifier));
	int y = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));
	std::string tVar("t");

	if(x < 0)
	{
		if((yyvsp[-2].identifier)->compare(tVar) == 0)
		{
			x = -1;
		}
		else
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-2].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
	}

	if(y < 0)
	{
		if((yyvsp[0].identifier)->compare(tVar) == 0)
		{
			y = -1;
		}
		else
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
	}

	continuousProblem.outputAxes.push_back(x);
	continuousProblem.outputAxes.push_back(y);
	continuousProblem.plotSetting = PLOT_GRID;
	continuousProblem.numSections = (int)(yyvsp[-3].dblVal);
	continuousProblem.plotFormat = PLOT_MATLAB;

	hybridProblem.outputAxes.push_back(x);
	hybridProblem.outputAxes.push_back(y);
	hybridProblem.plotSetting = PLOT_GRID;
	hybridProblem.numSections = (int)(yyvsp[-3].dblVal);
	hybridProblem.plotFormat = PLOT_MATLAB;

	delete (yyvsp[-2].identifier);
	delete (yyvsp[0].identifier);
}
#line 5908 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 146:
#line 3685 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.pFlowpipe) = new flowstar::Flowpipe(*(yyvsp[-1].tmVec), *(yyvsp[0].intVec));

	delete (yyvsp[-1].tmVec);
	delete (yyvsp[0].intVec);
}
#line 5919 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 147:
#line 3693 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Interval intZero;
	(yyval.pFlowpipe) = new flowstar::Flowpipe(*(yyvsp[0].intVec), intZero);

	delete (yyvsp[0].intVec);
}
#line 5930 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 148:
#line 3701 "modelParser.y" /* yacc.c:1648  */
    {
	initialSets = *(yyvsp[0].pVecFlowpipe);
	(yyval.pFlowpipe) = NULL;

	delete (yyvsp[0].pVecFlowpipe);
}
#line 5941 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 149:
#line 3710 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Interval intZero;
	flowstar::Flowpipe flowpipe(*(yyvsp[-1].intVec), intZero);

	(*(yyval.pVecFlowpipe)).push_back(flowpipe);

	delete (yyvsp[-1].intVec);
}
#line 5954 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 150:
#line 3720 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.pVecFlowpipe) = new std::vector<flowstar::Flowpipe>(1);

	flowstar::Interval intZero;
	flowstar::Flowpipe flowpipe(*(yyvsp[-1].intVec), intZero);
	(*(yyval.pVecFlowpipe))[0] = flowpipe;

	delete (yyvsp[-1].intVec);
}
#line 5968 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 151:
#line 3732 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 5975 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 152:
#line 3737 "modelParser.y" /* yacc.c:1648  */
    {
	int id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));

	if(id != -1)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "%s has already been declared as a state variable.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	id = continuousProblem.getIDForPar(*(yyvsp[0].identifier));

	if(id != -1)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "%s has already been declared as a parameter.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	if(!continuousProblem.declareTMVar(*(yyvsp[0].identifier)))
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "TM variable %s has already been declared.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	hybridProblem.declareTMVar(*(yyvsp[0].identifier));
	delete (yyvsp[0].identifier);
}
#line 6012 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 153:
#line 3771 "modelParser.y" /* yacc.c:1648  */
    {
	std::string tVar("local_t");
	continuousProblem.declareTMVar(tVar);
	hybridProblem.declareTMVar(tVar);

	int id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));

	if(id != -1)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "%s has already been declared as a state variable.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	id = continuousProblem.getIDForPar(*(yyvsp[0].identifier));

	if(id != -1)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "%s has already been declared as a parameter.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	if(!continuousProblem.declareTMVar(*(yyvsp[0].identifier)))
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "TM variable %s has already been declared.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	hybridProblem.declareTMVar(*(yyvsp[0].identifier));
	delete (yyvsp[0].identifier);
}
#line 6053 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 154:
#line 3811 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 6060 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 155:
#line 3816 "modelParser.y" /* yacc.c:1648  */
    {
	if(!varlist.declareVar(*(yyvsp[0].identifier)))
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "Variable %s has already been declared.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	delete (yyvsp[0].identifier);
}
#line 6076 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 156:
#line 3829 "modelParser.y" /* yacc.c:1648  */
    {
	varlist.clear();

	std::string tVar("local_t");
	varlist.declareVar(tVar);

	if(!varlist.declareVar(*(yyvsp[0].identifier)))
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "Variable %s has already been declared.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	delete (yyvsp[0].identifier);
}
#line 6097 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 157:
#line 3849 "modelParser.y" /* yacc.c:1648  */
    {
	int id = continuousProblem.getIDForStateVar(*(yyvsp[-8].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-8].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	if((yyvsp[-3].dblVal) > (yyvsp[-1].dblVal))
	{
		parseError("Invalid interval remainder.", lineNum);
		exit(1);
	}

	flowstar::Interval I((yyvsp[-3].dblVal),(yyvsp[-1].dblVal));
	flowstar::TaylorModel tmTemp(*(yyvsp[-6].poly), I);
	(yyval.tmVec) = (yyvsp[-9].tmVec);
	(yyval.tmVec)->tms[id] = tmTemp;

	delete (yyvsp[-8].identifier);
	delete (yyvsp[-6].poly);
}
#line 6127 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 158:
#line 3875 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::TaylorModel tmEmpty;
	(yyval.tmVec) = new flowstar::TaylorModelVec;

	for(int i=0; i<continuousProblem.stateVarNames.size(); ++i)
	{
		(yyval.tmVec)->tms.push_back(tmEmpty);
	}
}
#line 6141 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 159:
#line 3887 "modelParser.y" /* yacc.c:1648  */
    {
	if(continuousProblem.tmVarNames.size() == 0)
	{
		int id = varlist.getIDForVar(*(yyvsp[-6].identifier));

		if(id < 0)
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "Variable %s is not declared.", (*(yyvsp[-6].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}

		if((yyvsp[-3].dblVal) > (yyvsp[-1].dblVal))
		{
			parseError("Invalid interval.", lineNum);
			exit(1);
		}

		flowstar::Interval I((yyvsp[-3].dblVal),(yyvsp[-1].dblVal));
		(yyval.intVec) = (yyvsp[-7].intVec);
		(*(yyval.intVec))[id] = I;
	}
	else
	{
		int id = continuousProblem.getIDForTMVar(*(yyvsp[-6].identifier));

		if(id < 0)
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "TM variable %s is not declared.", (*(yyvsp[-6].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}

		if((yyvsp[-3].dblVal) > (yyvsp[-1].dblVal))
		{
			parseError("Invalid interval.", lineNum);
			exit(1);
		}

		flowstar::Interval I((yyvsp[-3].dblVal),(yyvsp[-1].dblVal));
		(yyval.intVec) = (yyvsp[-7].intVec);
		(*(yyval.intVec))[id] = I;
	}

	delete (yyvsp[-6].identifier);
}
#line 6194 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 160:
#line 3937 "modelParser.y" /* yacc.c:1648  */
    {
	if(continuousProblem.tmVarNames.size() == 0)
	{
		(yyval.intVec) = new std::vector<flowstar::Interval>( varlist.varNames.size() );

		flowstar::Interval intZero;
		(*(yyval.intVec))[0] = intZero;

		int id = varlist.getIDForVar(*(yyvsp[-6].identifier));

		if(id < 0)
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "Variable %s is not declared.", (*(yyvsp[-6].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}

		if((yyvsp[-3].dblVal) > (yyvsp[-1].dblVal))
		{
			parseError("Invalid interval.", lineNum);
			exit(1);
		}

		flowstar::Interval I((yyvsp[-3].dblVal),(yyvsp[-1].dblVal));
		(*(yyval.intVec))[id] = I;
	}
	else
	{
		(yyval.intVec) = new std::vector<flowstar::Interval>( continuousProblem.tmVarNames.size() );

		flowstar::Interval intZero;
		(*(yyval.intVec))[0] = intZero;

		int id = continuousProblem.getIDForTMVar(*(yyvsp[-6].identifier));

		if(id < 0)
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "TM variable %s is not declared.", (*(yyvsp[-6].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}

		if((yyvsp[-3].dblVal) > (yyvsp[-1].dblVal))
		{
			parseError("Invalid interval.", lineNum);
			exit(1);
		}

		flowstar::Interval I((yyvsp[-3].dblVal),(yyvsp[-1].dblVal));
		(*(yyval.intVec))[id] = I;
	}

	delete (yyvsp[-6].identifier);
}
#line 6255 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 161:
#line 3996 "modelParser.y" /* yacc.c:1648  */
    {
	int id = continuousProblem.getIDForStateVar(*(yyvsp[-6].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-6].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	if((yyvsp[-3].dblVal) > (yyvsp[-1].dblVal))
	{
		parseError("Invalid interval.", lineNum);
		exit(1);
	}

	flowstar::Interval I((yyvsp[-3].dblVal),(yyvsp[-1].dblVal));
	(yyval.intVec) = (yyvsp[-7].intVec);
	(*(yyval.intVec))[id] = I;

	delete (yyvsp[-6].identifier);
}
#line 6283 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 162:
#line 4020 "modelParser.y" /* yacc.c:1648  */
    {
	int numVars = continuousProblem.stateVarNames.size();
	(yyval.intVec) = new std::vector<flowstar::Interval>(numVars);

	std::string tVar("local_t");
	continuousProblem.declareTMVar(tVar);

	char name[NAME_SIZE];

	for(int i=0; i<numVars; ++i)
	{
		sprintf(name, "%s%d", local_var_name, i+1);
		std::string tmVarName(name);
		continuousProblem.declareTMVar(tmVarName);
	}
}
#line 6304 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 163:
#line 4039 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.tmVec) = (yyvsp[-4].tmVec);

	int id = continuousProblem.getIDForStateVar(*(yyvsp[-3].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-3].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	flowstar::Interval intZero;
	flowstar::TaylorModel tmTemp(*(yyvsp[0].poly), intZero);
	(yyval.tmVec)->tms[id] = tmTemp;

	delete (yyvsp[-3].identifier);
	delete (yyvsp[0].poly);
}
#line 6329 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 164:
#line 4060 "modelParser.y" /* yacc.c:1648  */
    {
	int numVars = continuousProblem.stateVarNames.size();

	(yyval.tmVec) = new flowstar::TaylorModelVec;
	flowstar::TaylorModel tmTemp;
	flowstar::Interval intZero;

	for(int i=0; i<numVars; ++i)
	{
		(yyval.tmVec)->tms.push_back(tmTemp);
	}
}
#line 6346 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 165:
#line 4075 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.strVec) = (yyvsp[-4].strVec);

	int id = continuousProblem.getIDForStateVar(*(yyvsp[-3].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-3].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	(*(yyval.strVec))[id] = (*(yyvsp[0].identifier));

	delete (yyvsp[-3].identifier);
	delete (yyvsp[0].identifier);
}
#line 6369 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 166:
#line 4094 "modelParser.y" /* yacc.c:1648  */
    {
	int numVars = continuousProblem.stateVarNames.size();
	(yyval.strVec) = new std::vector<std::string>;

	std::string empty;
	flowstar::Interval intZero;

	for(int i=0; i<numVars; ++i)
	{
		(yyval.strVec)->push_back(empty);
	}
}
#line 6386 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 167:
#line 4110 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 6393 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 168:
#line 4114 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 6400 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 169:
#line 4118 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 6407 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 170:
#line 4122 "modelParser.y" /* yacc.c:1648  */
    {
}
#line 6414 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 171:
#line 4128 "modelParser.y" /* yacc.c:1648  */
    {
	int id = continuousProblem.getIDForStateVar(*(yyvsp[-3].identifier));
	flowstar::Interval intZero;

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-3].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	for(int i=0; i<dyn_A_row.cols(); ++i)
	{
		dyn_A[id][i] = dyn_A_row[0][i];
		dyn_A_row[0][i] = intZero;
	}

	dyn_B[id][0] = dyn_B_row[0][0];
	dyn_B_row[0][0] = intZero;

	for(int i=0; i<dyn_ti_row.cols(); ++i)
	{
		dyn_ti[id][i] = dyn_ti_row[0][i];
		dyn_ti_row[0][i] = intZero;
	}

	for(int i=0; i<dyn_tv_row.cols(); ++i)
	{
		dyn_tv[id][i] = dyn_tv_row[0][i];
		dyn_tv_row[0][i] = intZero;
	}

	delete (yyvsp[-3].identifier);
}
#line 6454 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 172:
#line 4164 "modelParser.y" /* yacc.c:1648  */
    {
	int numVars = (int)continuousProblem.stateVarNames.size();
	int numTIPar = (int)continuousProblem.TI_Par_Names.size();
	int numTVPar = (int)continuousProblem.TV_Par_Names.size();

	flowstar::iMatrix im_A(numVars, numVars), im_B(numVars, 1), im_ti(numVars, numTIPar), im_tv(numVars, numTVPar);
	flowstar::iMatrix im_A_row(1, numVars), im_B_row(1,1), im_ti_row(1, numTIPar), im_tv_row(1, numTVPar);

	dyn_A = im_A;
	dyn_B = im_B;
	dyn_ti = im_ti;
	dyn_tv = im_tv;

	dyn_A_row = im_A_row;
	dyn_B_row = im_B_row;
	dyn_ti_row = im_ti_row;
	dyn_tv_row = im_tv_row;
}
#line 6477 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 173:
#line 4186 "modelParser.y" /* yacc.c:1648  */
    {
	int id = continuousProblem.getIDForStateVar(*(yyvsp[-3].identifier));
	flowstar::Interval intZero;

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-3].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	for(int i=0; i<dyn_A_row.cols(); ++i)
	{
		dyn_A[id][i] = dyn_A_row[0][i];
		dyn_A_row[0][i] = intZero;
	}

	dyn_B[id][0] = dyn_B_row[0][0];
	dyn_B_row[0][0] = intZero;
/*
	for(int i=0; i<dyn_ti_row.cols(); ++i)
	{
		dyn_ti[id][i] = dyn_ti_row[0][i];
		dyn_ti_row[0][i] = intZero;
	}

	for(int i=0; i<dyn_tv_row.cols(); ++i)
	{
		dyn_tv[id][i] = dyn_tv_row[0][i];
		dyn_tv_row[0][i] = intZero;
	}
*/
	delete (yyvsp[-3].identifier);
}
#line 6517 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 174:
#line 4222 "modelParser.y" /* yacc.c:1648  */
    {
	int numVars = (int)hybridProblem.stateVarNames.size();

	flowstar::iMatrix im_A(numVars, numVars), im_B(numVars, 1);
	flowstar::iMatrix im_A_row(1, numVars), im_B_row(1,1);

	dyn_A = im_A;
	dyn_B = im_B;

	dyn_A_row = im_A_row;
	dyn_B_row = im_B_row;
}
#line 6534 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 175:
#line 4239 "modelParser.y" /* yacc.c:1648  */
    {
	continuousProblem.maxNumSteps = -1;
}
#line 6542 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 176:
#line 4244 "modelParser.y" /* yacc.c:1648  */
    {
	continuousProblem.maxNumSteps = (yyvsp[-6].dblVal);
}
#line 6550 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 177:
#line 4249 "modelParser.y" /* yacc.c:1648  */
    {
	continuousProblem.maxNumSteps = -1;
}
#line 6558 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 178:
#line 4254 "modelParser.y" /* yacc.c:1648  */
    {
	continuousProblem.maxNumSteps = -1;
}
#line 6566 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 179:
#line 4259 "modelParser.y" /* yacc.c:1648  */
    {
	continuousProblem.maxNumSteps = (yyvsp[-6].dblVal);
}
#line 6574 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 180:
#line 4264 "modelParser.y" /* yacc.c:1648  */
    {
	continuousProblem.maxNumSteps = -1;
}
#line 6582 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 181:
#line 4271 "modelParser.y" /* yacc.c:1648  */
    {
	int id = continuousProblem.getIDForStateVar(*(yyvsp[-3].identifier));
	flowstar::UnivariatePolynomial polyZero;

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-3].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	for(int i=0; i<dyn_A_t_row.cols(); ++i)
	{
		dyn_A_t[id][i] = dyn_A_t_row[0][i];
		dyn_A_t_row[0][i] = polyZero;
	}

	dyn_B_t[id][0] = dyn_B_t_row[0][0];
	dyn_B_t_row[0][0] = polyZero;

	for(int i=0; i<dyn_ti_t_row.cols(); ++i)
	{
		dyn_ti_t[id][i] = dyn_ti_t_row[0][i];
		dyn_ti_t_row[0][i] = polyZero;
	}

	for(int i=0; i<dyn_tv_t_row.cols(); ++i)
	{
		dyn_tv_t[id][i] = dyn_tv_t_row[0][i];
		dyn_tv_t_row[0][i] = polyZero;
	}

	delete (yyvsp[-3].identifier);
}
#line 6622 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 182:
#line 4307 "modelParser.y" /* yacc.c:1648  */
    {
	int numVars = (int)continuousProblem.stateVarNames.size();
	int numTIPar = (int)continuousProblem.TI_Par_Names.size();
	int numTVPar = (int)continuousProblem.TV_Par_Names.size();

	flowstar::upMatrix upm_A_t(numVars, numVars), upm_B_t(numVars, 1), upm_ti_t(numVars, numTIPar), upm_tv_t(numVars, numTVPar);
	flowstar::upMatrix upm_A_t_row(1, numVars), upm_B_t_row(1,1), upm_ti_t_row(1, numTIPar), upm_tv_t_row(1, numTVPar);

	dyn_A_t = upm_A_t;
	dyn_B_t = upm_B_t;
	dyn_ti_t = upm_ti_t;
	dyn_tv_t = upm_tv_t;

	dyn_A_t_row = upm_A_t_row;
	dyn_B_t_row = upm_B_t_row;
	dyn_ti_t_row = upm_ti_t_row;
	dyn_tv_t_row = upm_tv_t_row;
}
#line 6645 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 183:
#line 4329 "modelParser.y" /* yacc.c:1648  */
    {
	int id = continuousProblem.getIDForStateVar(*(yyvsp[-3].identifier));
	flowstar::UnivariatePolynomial polyZero;

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-3].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	for(int i=0; i<dyn_A_t_row.cols(); ++i)
	{
		dyn_A_t[id][i] = dyn_A_t_row[0][i];
		dyn_A_t_row[0][i] = polyZero;
	}

	dyn_B_t[id][0] = dyn_B_t_row[0][0];
	dyn_B_t_row[0][0] = polyZero;

	delete (yyvsp[-3].identifier);
}
#line 6673 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 184:
#line 4353 "modelParser.y" /* yacc.c:1648  */
    {
	int numVars = (int)continuousProblem.stateVarNames.size();

	flowstar::upMatrix upm_A_t(numVars, numVars), upm_B_t(numVars, 1);
	flowstar::upMatrix upm_A_t_row(1, numVars), upm_B_t_row(1,1);

	dyn_A_t = upm_A_t;
	dyn_B_t = upm_B_t;

	dyn_A_t_row = upm_A_t_row;
	dyn_B_t_row = upm_B_t_row;
}
#line 6690 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 185:
#line 4381 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-2].poly);
	(*(yyval.poly)) += (*(yyvsp[0].poly));

	delete (yyvsp[0].poly);
}
#line 6701 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 186:
#line 4389 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-2].poly);
	(*(yyval.poly)) -= (*(yyvsp[0].poly));

	delete (yyvsp[0].poly);
}
#line 6712 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 187:
#line 4397 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-1].poly);
}
#line 6720 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 188:
#line 4402 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-2].poly);
	(*(yyval.poly)) *= (*(yyvsp[0].poly));

	delete (yyvsp[0].poly);
}
#line 6731 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 189:
#line 4410 "modelParser.y" /* yacc.c:1648  */
    {
	int exp = (int) (yyvsp[0].dblVal);

	if(exp == 0)
	{
		flowstar::Interval I(1);
		(yyval.poly) = new flowstar::Polynomial(I, continuousProblem.tmVarNames.size());
	}
	else
	{
		(yyval.poly) = new flowstar::Polynomial;
		(*(yyvsp[-2].poly)).pow(*(yyval.poly), exp);
	}

	delete (yyvsp[-2].poly);
}
#line 6752 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 190:
#line 4428 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Interval I(-1);
	(yyval.poly) = (yyvsp[0].poly);
	(yyval.poly)->mul_assign(I);
}
#line 6762 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 191:
#line 4435 "modelParser.y" /* yacc.c:1648  */
    {
	int id = continuousProblem.getIDForTMVar(*(yyvsp[0].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "TM variable %s is not declared.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	int numVars = continuousProblem.tmVarNames.size();
	flowstar::Interval I(1);

	std::vector<int> degrees;
	for(int i=0; i<numVars; ++i)
	{
		degrees.push_back(0);
	}

	degrees[id] = 1;
	flowstar::Monomial monomial(I, degrees);

	(yyval.poly) = new flowstar::Polynomial(monomial);
	delete (yyvsp[0].identifier);
}
#line 6793 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 192:
#line 4463 "modelParser.y" /* yacc.c:1648  */
    {
	int numVars = continuousProblem.tmVarNames.size();
	flowstar::Interval I((yyvsp[0].dblVal));
	(yyval.poly) = new flowstar::Polynomial(I, numVars);
}
#line 6803 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 193:
#line 4481 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-2].poly);
	(*(yyval.poly)) += (*(yyvsp[0].poly));

	delete (yyvsp[0].poly);
}
#line 6814 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 194:
#line 4489 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-2].poly);
	(*(yyval.poly)) -= (*(yyvsp[0].poly));

	delete (yyvsp[0].poly);
}
#line 6825 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 195:
#line 4497 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-1].poly);
}
#line 6833 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 196:
#line 4502 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-2].poly);
	(*(yyval.poly)) *= (*(yyvsp[0].poly));

	delete (yyvsp[0].poly);
}
#line 6844 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 197:
#line 4510 "modelParser.y" /* yacc.c:1648  */
    {
	int exp = (int) (yyvsp[0].dblVal);

	if(exp == 0)
	{
		flowstar::Interval I(1);
		(yyval.poly) = new flowstar::Polynomial(I, continuousProblem.stateVarNames.size()+1);
	}
	else
	{
		(yyval.poly) = new flowstar::Polynomial;
		(*(yyvsp[-2].poly)).pow(*(yyval.poly), exp);
	}

	delete (yyvsp[-2].poly);
}
#line 6865 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 198:
#line 4528 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Interval I(-1);
	(yyval.poly) = (yyvsp[0].poly);
	(yyval.poly)->mul_assign(I);
}
#line 6875 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 199:
#line 4535 "modelParser.y" /* yacc.c:1648  */
    {
	int id = continuousProblem.getIDForPar(*(yyvsp[0].identifier));

	if(id >= 0)
	{
		flowstar::Interval range;
		continuousProblem.getRangeForPar(range, *(yyvsp[0].identifier));

		int numVars = continuousProblem.stateVarNames.size()+1;
		(yyval.poly) = new flowstar::Polynomial(range, numVars);
	}
	else
	{
		id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));

		if(id < 0)
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}

		int numVars = continuousProblem.stateVarNames.size()+1;
		flowstar::Interval I(1);

		std::vector<int> degrees;
		for(int i=0; i<numVars; ++i)
		{
			degrees.push_back(0);
		}

		degrees[id+1] = 1;
		flowstar::Monomial monomial(I, degrees);

		(yyval.poly) = new flowstar::Polynomial(monomial);
	}

	delete (yyvsp[0].identifier);
}
#line 6920 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 200:
#line 4577 "modelParser.y" /* yacc.c:1648  */
    {
	int numVars = continuousProblem.stateVarNames.size()+1;
	flowstar::Interval I((yyvsp[-3].dblVal), (yyvsp[-1].dblVal));
	(yyval.poly) = new flowstar::Polynomial(I, numVars);
}
#line 6930 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 201:
#line 4584 "modelParser.y" /* yacc.c:1648  */
    {
	int numVars = continuousProblem.stateVarNames.size()+1;
	flowstar::Interval I((yyvsp[0].dblVal));
	(yyval.poly) = new flowstar::Polynomial(I, numVars);
}
#line 6940 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 202:
#line 4594 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-2].poly);
	(*(yyval.poly)) += (*(yyvsp[0].poly));

	delete (yyvsp[0].poly);
}
#line 6951 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 203:
#line 4602 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-2].poly);
	(*(yyval.poly)) -= (*(yyvsp[0].poly));

	delete (yyvsp[0].poly);
}
#line 6962 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 204:
#line 4610 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-1].poly);
}
#line 6970 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 205:
#line 4615 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-2].poly);
	(*(yyval.poly)) *= (*(yyvsp[0].poly));

	delete (yyvsp[0].poly);
}
#line 6981 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 206:
#line 4623 "modelParser.y" /* yacc.c:1648  */
    {
	int exp = (int) (yyvsp[0].dblVal);

	if(exp == 0)
	{
		flowstar::Interval I(1);
		(yyval.poly) = new flowstar::Polynomial(I, continuousProblem.stateVarNames.size()+1);
	}
	else
	{
		(yyval.poly) = new flowstar::Polynomial;
		(*(yyvsp[-2].poly)).pow(*(yyval.poly), exp);
	}

	delete (yyvsp[-2].poly);
}
#line 7002 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 207:
#line 4641 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Interval I(-1);
	(yyval.poly) = (yyvsp[0].poly);
	(yyval.poly)->mul_assign(I);
}
#line 7012 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 208:
#line 4648 "modelParser.y" /* yacc.c:1648  */
    {
	int id = continuousProblem.getIDForPar(*(yyvsp[0].identifier));

	if(id >= 0)
	{
		flowstar::Interval range;
		continuousProblem.getRangeForPar(range, *(yyvsp[0].identifier));

		int numVars = continuousProblem.stateVarNames.size()+1;
		(yyval.poly) = new flowstar::Polynomial(range, numVars);
	}
	else
	{
		id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));

		if(id < 0)
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}

		int numVars = continuousProblem.stateVarNames.size()+1;
		flowstar::Interval I(1);

		std::vector<int> degrees;
		for(int i=0; i<numVars; ++i)
		{
			degrees.push_back(0);
		}

		degrees[id+1] = 1;
		flowstar::Monomial monomial(I, degrees);

		(yyval.poly) = new flowstar::Polynomial(monomial);
	}

	delete (yyvsp[0].identifier);
}
#line 7057 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 209:
#line 4690 "modelParser.y" /* yacc.c:1648  */
    {
	int numVars = continuousProblem.stateVarNames.size()+1;
	flowstar::Interval I((yyvsp[0].dblVal));
	(yyval.poly) = new flowstar::Polynomial(I, numVars);
}
#line 7067 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 210:
#line 4701 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-2].poly);
	(*(yyval.poly)) += (*(yyvsp[0].poly));

	delete (yyvsp[0].poly);
}
#line 7078 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 211:
#line 4709 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-2].poly);
	(*(yyval.poly)) -= (*(yyvsp[0].poly));

	delete (yyvsp[0].poly);
}
#line 7089 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 212:
#line 4717 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-1].poly);
}
#line 7097 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 213:
#line 4722 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-2].poly);
	(*(yyval.poly)) *= (*(yyvsp[0].poly));

	delete (yyvsp[0].poly);
}
#line 7108 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 214:
#line 4730 "modelParser.y" /* yacc.c:1648  */
    {
	int exp = (int) (yyvsp[0].dblVal);

	if(exp == 0)
	{
		flowstar::Interval I(1);
		(yyval.poly) = new flowstar::Polynomial(I, continuousProblem.stateVarNames.size()+1);
	}
	else
	{
		(yyval.poly) = new flowstar::Polynomial;
		(*(yyvsp[-2].poly)).pow(*(yyval.poly), exp);
	}

	delete (yyvsp[-2].poly);
}
#line 7129 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 215:
#line 4748 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Interval I(-1);
	(yyval.poly) = (yyvsp[0].poly);
	(yyval.poly)->mul_assign(I);
}
#line 7139 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 216:
#line 4755 "modelParser.y" /* yacc.c:1648  */
    {
	int id = continuousProblem.getIDForPar(*(yyvsp[0].identifier));

	if(id >= 0)
	{
		flowstar::Interval range;
		continuousProblem.getRangeForPar(range, *(yyvsp[0].identifier));

		int numVars = continuousProblem.stateVarNames.size()+1;
		(yyval.poly) = new flowstar::Polynomial(range, numVars);
	}
	else
	{
		id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));

		if(id < 0)
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}

		int numVars = continuousProblem.stateVarNames.size()+1;
		flowstar::Interval I(1);

		std::vector<int> degrees;
		for(int i=0; i<numVars; ++i)
		{
			degrees.push_back(0);
		}

		degrees[id+1] = 1;
		flowstar::Monomial monomial(I, degrees);

		(yyval.poly) = new flowstar::Polynomial(monomial);
	}

	delete (yyvsp[0].identifier);
}
#line 7184 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 217:
#line 4797 "modelParser.y" /* yacc.c:1648  */
    {
	int numVars = continuousProblem.stateVarNames.size()+1;
	flowstar::Interval I((yyvsp[0].dblVal));
	(yyval.poly) = new flowstar::Polynomial(I, numVars);
}
#line 7194 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 218:
#line 4809 "modelParser.y" /* yacc.c:1648  */
    {
	int id = continuousProblem.getIDForStateVar(*(yyvsp[-8].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-8].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	if((yyvsp[-3].dblVal) > (yyvsp[-1].dblVal))
	{
		parseError("Invalid interval remainder.", lineNum);
		exit(1);
	}

	flowstar::Interval I((yyvsp[-3].dblVal),(yyvsp[-1].dblVal));
	flowstar::TaylorModel tmTemp(*(yyvsp[-6].poly), I);
	(yyval.tmVec) = (yyvsp[-9].tmVec);
	(yyval.tmVec)->tms[id] = tmTemp;

	delete (yyvsp[-8].identifier);
	delete (yyvsp[-6].poly);
}
#line 7224 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 219:
#line 4836 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::TaylorModel tmEmpty;
	(yyval.tmVec) = new flowstar::TaylorModelVec;

	for(int i=0; i<continuousProblem.stateVarNames.size(); ++i)
	{
		(yyval.tmVec)->tms.push_back(tmEmpty);
	}

	int id = continuousProblem.getIDForStateVar(*(yyvsp[-8].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[-8].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	if((yyvsp[-3].dblVal) > (yyvsp[-1].dblVal))
	{
		parseError("Invalid interval remainder.", lineNum);
		exit(1);
	}

	flowstar::Interval I((yyvsp[-3].dblVal),(yyvsp[-1].dblVal));
	flowstar::TaylorModel tmTemp(*(yyvsp[-6].poly), I);

	(yyval.tmVec)->tms[id] = tmTemp;

	delete (yyvsp[-8].identifier);
	delete (yyvsp[-6].poly);
}
#line 7262 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 220:
#line 4881 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-2].poly);
	(*(yyval.poly)) += (*(yyvsp[0].poly));

	delete (yyvsp[0].poly);
}
#line 7273 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 221:
#line 4889 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-2].poly);
	(*(yyval.poly)) -= (*(yyvsp[0].poly));

	delete (yyvsp[0].poly);
}
#line 7284 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 222:
#line 4897 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-1].poly);
}
#line 7292 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 223:
#line 4902 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-2].poly);
	(*(yyval.poly)) *= (*(yyvsp[0].poly));

	delete (yyvsp[0].poly);
}
#line 7303 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 224:
#line 4910 "modelParser.y" /* yacc.c:1648  */
    {
	int exp = (int) (yyvsp[0].dblVal);

	if(exp == 0)
	{
		flowstar::Interval I(1);
		(yyval.poly) = new flowstar::Polynomial(I, continuousProblem.tmVarNames.size());
	}
	else
	{
		(yyval.poly) = new flowstar::Polynomial;
		(*(yyvsp[-2].poly)).pow(*(yyval.poly), exp);
	}

	delete (yyvsp[-2].poly);
}
#line 7324 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 225:
#line 4928 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Interval I(-1);
	(yyval.poly) = (yyvsp[0].poly);
	(yyval.poly)->mul_assign(I);
}
#line 7334 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 226:
#line 4935 "modelParser.y" /* yacc.c:1648  */
    {
	if(continuousProblem.tmVarNames.size() == 0)
	{
		int id = varlist.getIDForVar(*(yyvsp[0].identifier));

		if(id < 0)
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "Variable %s is not declared.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}

		int numVars = varlist.varNames.size();
		flowstar::Interval I(1);

		std::vector<int> degrees;
		for(int i=0; i<numVars; ++i)
		{
			degrees.push_back(0);
		}

		degrees[id] = 1;
		flowstar::Monomial monomial(I, degrees);

		(yyval.poly) = new flowstar::Polynomial(monomial);
	}
	else
	{
		int id = continuousProblem.getIDForTMVar(*(yyvsp[0].identifier));

		if(id < 0)
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "TM variable %s is not declared.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}

		int numVars = continuousProblem.tmVarNames.size();
		flowstar::Interval I(1);

		std::vector<int> degrees;
		for(int i=0; i<numVars; ++i)
		{
			degrees.push_back(0);
		}

		degrees[id] = 1;
		flowstar::Monomial monomial(I, degrees);

		(yyval.poly) = new flowstar::Polynomial(monomial);
	}

	delete (yyvsp[0].identifier);
}
#line 7395 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 227:
#line 4993 "modelParser.y" /* yacc.c:1648  */
    {
	if(continuousProblem.tmVarNames.size() == 0)
	{
		int numVars = varlist.varNames.size();
		flowstar::Interval I((yyvsp[-3].dblVal), (yyvsp[-1].dblVal));
		(yyval.poly) = new flowstar::Polynomial(I, numVars);
	}
	else
	{
		int numVars = continuousProblem.tmVarNames.size();
		flowstar::Interval I((yyvsp[-3].dblVal), (yyvsp[-1].dblVal));
		(yyval.poly) = new flowstar::Polynomial(I, numVars);
	}
}
#line 7414 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 228:
#line 5009 "modelParser.y" /* yacc.c:1648  */
    {
	if(continuousProblem.tmVarNames.size() == 0)
	{
		int numVars = varlist.varNames.size();
		flowstar::Interval I((yyvsp[0].dblVal));
		(yyval.poly) = new flowstar::Polynomial(I, numVars);
	}
	else
	{
		int numVars = continuousProblem.tmVarNames.size();
		flowstar::Interval I((yyvsp[0].dblVal));
		(yyval.poly) = new flowstar::Polynomial(I, numVars);
	}
}
#line 7433 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 229:
#line 5045 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.ptm) = (yyvsp[-2].ptm);
	(yyvsp[-2].ptm)->add_assign(*(yyvsp[0].ptm));
	delete (yyvsp[0].ptm);
}
#line 7443 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 230:
#line 5052 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.ptm) = (yyvsp[-2].ptm);
	(yyvsp[-2].ptm)->sub_assign(*(yyvsp[0].ptm));
	delete (yyvsp[0].ptm);
}
#line 7453 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 231:
#line 5059 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.ptm) = (yyvsp[-2].ptm);

	flowstar::Interval intPoly1, intPoly2, intTrunc;

	(yyvsp[0].ptm)->polyRangeNormal(intPoly2, parseSetting.step_exp_table);
	(yyvsp[-2].ptm)->mul_insert_ctrunc_normal_assign(intPoly1, intTrunc, *(yyvsp[0].ptm), intPoly2, parseSetting.step_exp_table, parseSetting.order, parseSetting.cutoff_threshold);

	parseSetting.ranges.push_back(intPoly1);
	parseSetting.ranges.push_back(intPoly2);
	parseSetting.ranges.push_back(intTrunc);

	delete (yyvsp[0].ptm);
}
#line 7472 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 232:
#line 5075 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.ptm) = (yyvsp[-1].ptm);
}
#line 7480 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 233:
#line 5080 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::TaylorModel tmTemp;
	(yyvsp[0].ptm)->rec_taylor(tmTemp, parseSetting.ranges, parseSetting.step_exp_table, continuousProblem.stateVarNames.size()+1, parseSetting.order, parseSetting.cutoff_threshold);

	(yyval.ptm) = (yyvsp[-2].ptm);

	flowstar::Interval intPoly1, intPoly2, intTrunc;

	tmTemp.polyRangeNormal(intPoly2, parseSetting.step_exp_table);
	(yyvsp[-2].ptm)->mul_insert_ctrunc_normal_assign(intPoly1, intTrunc, tmTemp, intPoly2, parseSetting.step_exp_table, parseSetting.order, parseSetting.cutoff_threshold);

	parseSetting.ranges.push_back(intPoly1);
	parseSetting.ranges.push_back(intPoly2);
	parseSetting.ranges.push_back(intTrunc);

	delete (yyvsp[0].ptm);
}
#line 7502 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 234:
#line 5099 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::TaylorModel tmTemp;
	(yyvsp[-1].ptm)->exp_taylor(tmTemp, parseSetting.ranges, parseSetting.step_exp_table, continuousProblem.stateVarNames.size()+1, parseSetting.order, parseSetting.cutoff_threshold);

	*(yyvsp[-1].ptm) = tmTemp;
	(yyval.ptm) = (yyvsp[-1].ptm);
}
#line 7514 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 235:
#line 5108 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::TaylorModel tmTemp;
	(yyvsp[-1].ptm)->sin_taylor(tmTemp, parseSetting.ranges, parseSetting.step_exp_table, continuousProblem.stateVarNames.size()+1, parseSetting.order, parseSetting.cutoff_threshold);

	*(yyvsp[-1].ptm) = tmTemp;
	(yyval.ptm) = (yyvsp[-1].ptm);
}
#line 7526 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 236:
#line 5117 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::TaylorModel tmTemp;
	(yyvsp[-1].ptm)->cos_taylor(tmTemp, parseSetting.ranges, parseSetting.step_exp_table, continuousProblem.stateVarNames.size()+1, parseSetting.order, parseSetting.cutoff_threshold);

	*(yyvsp[-1].ptm) = tmTemp;
	(yyval.ptm) = (yyvsp[-1].ptm);
}
#line 7538 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 237:
#line 5126 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::TaylorModel tmTemp;
	(yyvsp[-1].ptm)->log_taylor(tmTemp, parseSetting.ranges, parseSetting.step_exp_table, continuousProblem.stateVarNames.size()+1, parseSetting.order, parseSetting.cutoff_threshold);

	*(yyvsp[-1].ptm) = tmTemp;
	(yyval.ptm) = (yyvsp[-1].ptm);
}
#line 7550 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 238:
#line 5135 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::TaylorModel tmTemp;
	(yyvsp[-1].ptm)->sqrt_taylor(tmTemp, parseSetting.ranges, parseSetting.step_exp_table, continuousProblem.stateVarNames.size()+1, parseSetting.order, parseSetting.cutoff_threshold);

	*(yyvsp[-1].ptm) = tmTemp;
	(yyval.ptm) = (yyvsp[-1].ptm);
}
#line 7562 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 239:
#line 5144 "modelParser.y" /* yacc.c:1648  */
    {
	int exp = (int)(yyvsp[0].dblVal);

	if(exp == 0)
	{
		flowstar::Interval I(1);
		(yyval.ptm) = new flowstar::TaylorModel(I, continuousProblem.stateVarNames.size()+1);
	}
	else
	{
		flowstar::TaylorModel res = *(yyvsp[-2].ptm);
		flowstar::TaylorModel pow = *(yyvsp[-2].ptm);

		flowstar::Interval intPoly1, intPoly2, intTrunc;

		for(int degree = exp - 1; degree > 0;)
		{
			pow.polyRangeNormal(intPoly2, parseSetting.step_exp_table);

			if(degree & 1)
			{
				res.mul_insert_ctrunc_normal_assign(intPoly1, intTrunc, pow, intPoly2, parseSetting.step_exp_table, parseSetting.order, parseSetting.cutoff_threshold);

				parseSetting.ranges.push_back(intPoly1);
				parseSetting.ranges.push_back(intPoly2);
				parseSetting.ranges.push_back(intTrunc);
			}

			degree >>= 1;

			if(degree > 0)
			{
				pow.mul_insert_ctrunc_normal_assign(intPoly1, intTrunc, pow, intPoly2, parseSetting.step_exp_table, parseSetting.order, parseSetting.cutoff_threshold);

				parseSetting.ranges.push_back(intPoly1);
				parseSetting.ranges.push_back(intPoly2);
				parseSetting.ranges.push_back(intTrunc);
			}
		}

		(yyval.ptm) = new flowstar::TaylorModel(res);
	}

	delete (yyvsp[-2].ptm);
}
#line 7612 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 240:
#line 5191 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Interval I(-1);
	(yyval.ptm) = (yyvsp[0].ptm);
	(yyval.ptm)->mul_assign(I);
}
#line 7622 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 241:
#line 5198 "modelParser.y" /* yacc.c:1648  */
    {
	int id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	(yyval.ptm) = new flowstar::TaylorModel;
	(*(yyval.ptm)) = parseSetting.flowpipe.tms[id];

	flowstar::Interval intTemp;
	(*(yyval.ptm)).expansion.ctrunc_normal(intTemp, parseSetting.step_exp_table, parseSetting.order);
	parseSetting.ranges.push_back(intTemp);
	(*(yyval.ptm)).remainder += intTemp;

	delete (yyvsp[0].identifier);
}
#line 7648 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 242:
#line 5221 "modelParser.y" /* yacc.c:1648  */
    {
	int numVars = continuousProblem.stateVarNames.size()+1;
	flowstar::Interval I((yyvsp[-3].dblVal), (yyvsp[-1].dblVal));
	(yyval.ptm) = new flowstar::TaylorModel(I, numVars);
}
#line 7658 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 243:
#line 5255 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.pint) = (yyvsp[-2].pint);
	(*(yyval.pint)) += (*(yyvsp[0].pint));
	delete (yyvsp[0].pint);
}
#line 7668 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 244:
#line 5262 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.pint) = (yyvsp[-2].pint);
	(*(yyval.pint)) -= (*(yyvsp[0].pint));
	delete (yyvsp[0].pint);
}
#line 7678 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 245:
#line 5269 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.pint) = new flowstar::Interval;

	(*(yyval.pint)) = (*parseSetting.iterRange) * (*(yyvsp[0].pint));
	++parseSetting.iterRange;
	(*(yyval.pint)) += (*parseSetting.iterRange) * (*(yyvsp[-2].pint));
	(*(yyval.pint)) += (*(yyvsp[-2].pint)) * (*(yyvsp[0].pint));
	++parseSetting.iterRange;
	(*(yyval.pint)) += (*parseSetting.iterRange);
	++parseSetting.iterRange;

	delete (yyvsp[-2].pint);
	delete (yyvsp[0].pint);
}
#line 7697 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 246:
#line 5285 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.pint) = (yyvsp[-1].pint);
}
#line 7705 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 247:
#line 5290 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Interval intTemp;
	rec_taylor_only_remainder(intTemp, *(yyvsp[0].pint), parseSetting.iterRange, parseSetting.order);

	(yyval.pint) = new flowstar::Interval;

	(*(yyval.pint)) = (*parseSetting.iterRange) * intTemp;
	++parseSetting.iterRange;
	(*(yyval.pint)) += (*parseSetting.iterRange) * (*(yyvsp[-2].pint));
	(*(yyval.pint)) += (*(yyvsp[-2].pint)) * intTemp;
	++parseSetting.iterRange;
	(*(yyval.pint)) += (*parseSetting.iterRange);
	++parseSetting.iterRange;

	delete (yyvsp[-2].pint);
	delete (yyvsp[0].pint);
}
#line 7727 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 248:
#line 5309 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Interval intTemp;
	exp_taylor_only_remainder(intTemp, *(yyvsp[-1].pint), parseSetting.iterRange, parseSetting.order);

	(*(yyvsp[-1].pint)) = intTemp;
	(yyval.pint) = (yyvsp[-1].pint);
}
#line 7739 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 249:
#line 5318 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Interval intTemp;
	sin_taylor_only_remainder(intTemp, *(yyvsp[-1].pint), parseSetting.iterRange, parseSetting.order);

	(*(yyvsp[-1].pint)) = intTemp;
	(yyval.pint) = (yyvsp[-1].pint);
}
#line 7751 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 250:
#line 5327 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Interval intTemp;
	cos_taylor_only_remainder(intTemp, *(yyvsp[-1].pint), parseSetting.iterRange, parseSetting.order);

	(*(yyvsp[-1].pint)) = intTemp;
	(yyval.pint) = (yyvsp[-1].pint);
}
#line 7763 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 251:
#line 5336 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Interval intTemp;
	log_taylor_only_remainder(intTemp, *(yyvsp[-1].pint), parseSetting.iterRange, parseSetting.order);

	(*(yyvsp[-1].pint)) = intTemp;
	(yyval.pint) = (yyvsp[-1].pint);
}
#line 7775 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 252:
#line 5345 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Interval intTemp;
	sqrt_taylor_only_remainder(intTemp, *(yyvsp[-1].pint), parseSetting.iterRange, parseSetting.order);

	(*(yyvsp[-1].pint)) = intTemp;
	(yyval.pint) = (yyvsp[-1].pint);
}
#line 7787 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 253:
#line 5354 "modelParser.y" /* yacc.c:1648  */
    {
	int exp = (int)(yyvsp[0].dblVal);

	if(exp == 0)
	{
		flowstar::Interval intZero;
		(*(yyvsp[-2].pint)) = intZero;
		(yyval.pint) = (yyvsp[-2].pint);
	}
	else
	{
		flowstar::Interval res(*(yyvsp[-2].pint));
		flowstar::Interval pow(*(yyvsp[-2].pint));

		flowstar::Interval intPoly1, intPoly2, intTrunc;

		for(int degree = exp - 1; degree > 0;)
		{
			if(degree & 1)
			{
				flowstar::Interval intTemp;
				intTemp = (*parseSetting.iterRange) * pow;
				++parseSetting.iterRange;
				intTemp += (*parseSetting.iterRange) * res;
				intTemp += pow * res;
				++parseSetting.iterRange;
				intTemp += (*parseSetting.iterRange);
				++parseSetting.iterRange;

				res = intTemp;
			}

			degree >>= 1;

			if(degree > 0)
			{
				flowstar::Interval intTemp;
				intTemp = (*parseSetting.iterRange) * pow;
				++parseSetting.iterRange;
				intTemp += (*parseSetting.iterRange) * pow;
				intTemp += pow * pow;
				++parseSetting.iterRange;
				intTemp += (*parseSetting.iterRange);
				++parseSetting.iterRange;

				pow = intTemp;
			}
		}

		(yyval.pint) = new flowstar::Interval(res);
	}

	delete (yyvsp[-2].pint);
}
#line 7846 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 254:
#line 5410 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.pint) = (yyvsp[0].pint);
	(yyval.pint)->inv_assign();
}
#line 7855 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 255:
#line 5416 "modelParser.y" /* yacc.c:1648  */
    {
	int id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	(yyval.pint) = new flowstar::Interval;
	(*(yyval.pint)) = parseSetting.flowpipe.tms[id].getRemainder();

	(*(yyval.pint)) += (*parseSetting.iterRange);
	++parseSetting.iterRange;

	delete (yyvsp[0].identifier);
}
#line 7879 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 256:
#line 5437 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.pint) = new flowstar::Interval;
}
#line 7887 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 257:
#line 5464 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-2].poly);
	(*(yyval.poly)) += (*(yyvsp[0].poly));

	delete (yyvsp[0].poly);
}
#line 7898 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 258:
#line 5472 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-2].poly);
	(*(yyval.poly)) -= (*(yyvsp[0].poly));

	delete (yyvsp[0].poly);
}
#line 7909 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 259:
#line 5480 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-2].poly);
	(*(yyval.poly)) *= (*(yyvsp[0].poly));
	(yyval.poly)->nctrunc(parseSetting.order);
	(yyval.poly)->cutoff(parseSetting.cutoff_threshold);

	delete (yyvsp[0].poly);
}
#line 7922 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 260:
#line 5490 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[-1].poly);
}
#line 7930 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 261:
#line 5495 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Polynomial polyTemp;
	(yyvsp[0].poly)->rec_taylor(polyTemp, continuousProblem.stateVarNames.size()+1, parseSetting.order, parseSetting.cutoff_threshold);

	(*(yyvsp[-2].poly)) *= polyTemp;
	(yyvsp[-2].poly)->nctrunc(parseSetting.order);
	(yyval.poly) = (yyvsp[-2].poly);
	(yyval.poly)->cutoff(parseSetting.cutoff_threshold);

	delete (yyvsp[0].poly);
}
#line 7946 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 262:
#line 5508 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Polynomial polyTemp;
	(yyvsp[-1].poly)->exp_taylor(polyTemp, continuousProblem.stateVarNames.size()+1, parseSetting.order, parseSetting.cutoff_threshold);

	(*(yyvsp[-1].poly)) = polyTemp;
	(yyval.poly) = (yyvsp[-1].poly);
}
#line 7958 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 263:
#line 5517 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Polynomial polyTemp;
	(yyvsp[-1].poly)->sin_taylor(polyTemp, continuousProblem.stateVarNames.size()+1, parseSetting.order, parseSetting.cutoff_threshold);

	(*(yyvsp[-1].poly)) = polyTemp;
	(yyval.poly) = (yyvsp[-1].poly);
}
#line 7970 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 264:
#line 5526 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Polynomial polyTemp;
	(yyvsp[-1].poly)->cos_taylor(polyTemp, continuousProblem.stateVarNames.size()+1, parseSetting.order, parseSetting.cutoff_threshold);

	(*(yyvsp[-1].poly)) = polyTemp;
	(yyval.poly) = (yyvsp[-1].poly);
}
#line 7982 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 265:
#line 5535 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Polynomial polyTemp;
	(yyvsp[-1].poly)->log_taylor(polyTemp, continuousProblem.stateVarNames.size()+1, parseSetting.order, parseSetting.cutoff_threshold);

	(*(yyvsp[-1].poly)) = polyTemp;
	(yyval.poly) = (yyvsp[-1].poly);
}
#line 7994 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 266:
#line 5544 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Polynomial polyTemp;
	(yyvsp[-1].poly)->sqrt_taylor(polyTemp, continuousProblem.stateVarNames.size()+1, parseSetting.order, parseSetting.cutoff_threshold);

	(*(yyvsp[-1].poly)) = polyTemp;
	(yyval.poly) = (yyvsp[-1].poly);
}
#line 8006 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 267:
#line 5553 "modelParser.y" /* yacc.c:1648  */
    {
	int exp = (int) (yyvsp[0].dblVal);

	(yyval.poly) = new flowstar::Polynomial;

	(*(yyvsp[-2].poly)).pow(*(yyval.poly), exp, parseSetting.order);
	(yyval.poly)->cutoff(parseSetting.cutoff_threshold);
}
#line 8019 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 268:
#line 5563 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.poly) = (yyvsp[0].poly);
	(yyval.poly)->inv_assign();
}
#line 8028 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 269:
#line 5569 "modelParser.y" /* yacc.c:1648  */
    {
	int id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[0].identifier)).c_str());
		parseError(errMsg, lineNum);
		exit(1);
	}

	(yyval.poly) = new flowstar::Polynomial;
	parseSetting.flowpipe.tms[id].getExpansion(*(yyval.poly));

	(*(yyval.poly)).nctrunc(parseSetting.order);
}
#line 8049 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 270:
#line 5587 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Interval I((yyvsp[-3].dblVal), (yyvsp[-1].dblVal));
	(yyval.poly) = new flowstar::Polynomial(I, continuousProblem.stateVarNames.size()+1);
}
#line 8058 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 271:
#line 5615 "modelParser.y" /* yacc.c:1648  */
    {
	(*(yyvsp[-2].identifier)) += ' ';
	(*(yyvsp[-2].identifier)) += '+';
	(*(yyvsp[-2].identifier)) += ' ';
	(*(yyvsp[-2].identifier)) += (*(yyvsp[0].identifier));

	(yyval.identifier) = (yyvsp[-2].identifier);
	delete (yyvsp[0].identifier);
}
#line 8072 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 272:
#line 5626 "modelParser.y" /* yacc.c:1648  */
    {
	(*(yyvsp[-2].identifier)) += ' ';
	(*(yyvsp[-2].identifier)) += '-';
	(*(yyvsp[-2].identifier)) += ' ';
	(*(yyvsp[-2].identifier)) += (*(yyvsp[0].identifier));

	(yyval.identifier) = (yyvsp[-2].identifier);
	delete (yyvsp[0].identifier);
}
#line 8086 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 273:
#line 5637 "modelParser.y" /* yacc.c:1648  */
    {
	(*(yyvsp[-2].identifier)) += ' ';
	(*(yyvsp[-2].identifier)) += '*';
	(*(yyvsp[-2].identifier)) += ' ';
	(*(yyvsp[-2].identifier)) += (*(yyvsp[0].identifier));

	(yyval.identifier) = (yyvsp[-2].identifier);
	delete (yyvsp[0].identifier);
}
#line 8100 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 274:
#line 5648 "modelParser.y" /* yacc.c:1648  */
    {
	std::string str;
	str += '(';
	str += (*(yyvsp[-1].identifier));
	str += ')';
	(*(yyvsp[-1].identifier)) = str;

	(yyval.identifier) = (yyvsp[-1].identifier);
}
#line 8114 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 275:
#line 5659 "modelParser.y" /* yacc.c:1648  */
    {
	(*(yyvsp[-2].identifier)) += ' ';
	(*(yyvsp[-2].identifier)) += '/';
	(*(yyvsp[-2].identifier)) += ' ';
	(*(yyvsp[-2].identifier)) += (*(yyvsp[0].identifier));

	(yyval.identifier) = (yyvsp[-2].identifier);
	delete (yyvsp[0].identifier);
}
#line 8128 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 276:
#line 5670 "modelParser.y" /* yacc.c:1648  */
    {
	std::string str("exp");
	str += '(';
	str += (*(yyvsp[-1].identifier));
	str += ')';
	(*(yyvsp[-1].identifier)) = str;

	(yyval.identifier) = (yyvsp[-1].identifier);
}
#line 8142 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 277:
#line 5681 "modelParser.y" /* yacc.c:1648  */
    {
	std::string str("sin");
	str += '(';
	str += (*(yyvsp[-1].identifier));
	str += ')';
	(*(yyvsp[-1].identifier)) = str;

	(yyval.identifier) = (yyvsp[-1].identifier);
}
#line 8156 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 278:
#line 5692 "modelParser.y" /* yacc.c:1648  */
    {
	std::string str("cos");
	str += '(';
	str += (*(yyvsp[-1].identifier));
	str += ')';
	(*(yyvsp[-1].identifier)) = str;

	(yyval.identifier) = (yyvsp[-1].identifier);
}
#line 8170 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 279:
#line 5703 "modelParser.y" /* yacc.c:1648  */
    {
	std::string str("log");
	str += '(';
	str += (*(yyvsp[-1].identifier));
	str += ')';
	(*(yyvsp[-1].identifier)) = str;

	(yyval.identifier) = (yyvsp[-1].identifier);
}
#line 8184 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 280:
#line 5714 "modelParser.y" /* yacc.c:1648  */
    {
	std::string str("sqrt");
	str += '(';
	str += (*(yyvsp[-1].identifier));
	str += ')';
	(*(yyvsp[-1].identifier)) = str;

	(yyval.identifier) = (yyvsp[-1].identifier);
}
#line 8198 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 281:
#line 5725 "modelParser.y" /* yacc.c:1648  */
    {
	(*(yyvsp[-2].identifier)) += '^';

	char strNum[NUM_LENGTH];
	sprintf(strNum, "%d", (int)(yyvsp[0].dblVal));
	std::string num(strNum);
	(*(yyvsp[-2].identifier)) += num;

	(yyval.identifier) = (yyvsp[-2].identifier);
}
#line 8213 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 282:
#line 5737 "modelParser.y" /* yacc.c:1648  */
    {
	std::string str;
	str += '-';
	str += (*(yyvsp[0].identifier));
	(*(yyvsp[0].identifier)) = str;

	(yyval.identifier) = (yyvsp[0].identifier);
}
#line 8226 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 283:
#line 5747 "modelParser.y" /* yacc.c:1648  */
    {
	int id = continuousProblem.getIDForPar(*(yyvsp[0].identifier));

	if(id >= 0)
	{
		flowstar::Interval range;
		continuousProblem.getRangeForPar(range, *(yyvsp[0].identifier));

		(yyval.identifier) = new std::string;
		range.toString(*(yyval.identifier));
	}
	else
	{
		id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));

		if(id < 0)
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "State variable %s is not declared.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}

		(yyval.identifier) = (yyvsp[0].identifier);
	}
}
#line 8257 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 284:
#line 5775 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.identifier) = new std::string;
	char strNum_lo[NUM_LENGTH], strNum_up[NUM_LENGTH];
	sprintf(strNum_lo, "%.20e", (yyvsp[-3].dblVal));
	sprintf(strNum_up, "%.20e", (yyvsp[-1].dblVal));

	std::string num_lo(strNum_lo);
	std::string num_up(strNum_up);

	(*(yyval.identifier)) += '[';
	(*(yyval.identifier)) += num_lo;
	(*(yyval.identifier)) += ' ';
	(*(yyval.identifier)) += ',';
	(*(yyval.identifier)) += ' ';
	(*(yyval.identifier)) += num_up;
	(*(yyval.identifier)) += ']';
}
#line 8279 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 285:
#line 5794 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.identifier) = new std::string;
	char strNum[NUM_LENGTH];
	sprintf(strNum, "%.20e", (yyvsp[0].dblVal));
	std::string num(strNum);

	(*(yyval.identifier)) += '[';
	(*(yyval.identifier)) += num;
	(*(yyval.identifier)) += ' ';
	(*(yyval.identifier)) += ',';
	(*(yyval.identifier)) += ' ';
	(*(yyval.identifier)) += num;
	(*(yyval.identifier)) += ']';
}
#line 8298 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 286:
#line 5828 "modelParser.y" /* yacc.c:1648  */
    {
	(yyvsp[-2].p_ODE_String)->ode += ' ';
	(yyvsp[-2].p_ODE_String)->ode += '+';
	(yyvsp[-2].p_ODE_String)->ode += ' ';
	(yyvsp[-2].p_ODE_String)->ode += (yyvsp[0].p_ODE_String)->ode;

	(yyval.p_ODE_String) = (yyvsp[-2].p_ODE_String);

	if(parseResult.bConstant)
	{
		(yyval.p_ODE_String)->constant = (yyvsp[-2].p_ODE_String)->constant + (yyvsp[0].p_ODE_String)->constant;
	}

	delete (yyvsp[0].p_ODE_String);
}
#line 8318 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 287:
#line 5845 "modelParser.y" /* yacc.c:1648  */
    {
	(yyvsp[-2].p_ODE_String)->ode += ' ';
	(yyvsp[-2].p_ODE_String)->ode += '-';
	(yyvsp[-2].p_ODE_String)->ode += ' ';
	(yyvsp[-2].p_ODE_String)->ode += (yyvsp[0].p_ODE_String)->ode;

	(yyval.p_ODE_String) = (yyvsp[-2].p_ODE_String);

	if(parseResult.bConstant)
	{
		(yyval.p_ODE_String)->constant = (yyvsp[-2].p_ODE_String)->constant - (yyvsp[0].p_ODE_String)->constant;
	}

	delete (yyvsp[0].p_ODE_String);
}
#line 8338 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 288:
#line 5862 "modelParser.y" /* yacc.c:1648  */
    {
	(yyvsp[-2].p_ODE_String)->ode += ' ';
	(yyvsp[-2].p_ODE_String)->ode += '*';
	(yyvsp[-2].p_ODE_String)->ode += ' ';
	(yyvsp[-2].p_ODE_String)->ode += (yyvsp[0].p_ODE_String)->ode;

	(yyval.p_ODE_String) = (yyvsp[-2].p_ODE_String);

	if(parseResult.bConstant)
	{
		(yyval.p_ODE_String)->constant = (yyvsp[-2].p_ODE_String)->constant * (yyvsp[0].p_ODE_String)->constant;
	}

	delete (yyvsp[0].p_ODE_String);
}
#line 8358 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 289:
#line 5879 "modelParser.y" /* yacc.c:1648  */
    {
	std::string str;
	str += '(';
	str += (yyvsp[-1].p_ODE_String)->ode;
	str += ')';
	(yyvsp[-1].p_ODE_String)->ode = str;

	(yyval.p_ODE_String) = (yyvsp[-1].p_ODE_String);
}
#line 8372 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 290:
#line 5890 "modelParser.y" /* yacc.c:1648  */
    {
	(yyvsp[-2].p_ODE_String)->ode += ' ';
	(yyvsp[-2].p_ODE_String)->ode += '/';
	(yyvsp[-2].p_ODE_String)->ode += ' ';
	(yyvsp[-2].p_ODE_String)->ode += (yyvsp[0].p_ODE_String)->ode;

	(yyval.p_ODE_String) = (yyvsp[-2].p_ODE_String);

	if(parseResult.bConstant)
	{
		(yyval.p_ODE_String)->constant = (yyvsp[-2].p_ODE_String)->constant / (yyvsp[0].p_ODE_String)->constant;
	}

	delete (yyvsp[0].p_ODE_String);
}
#line 8392 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 291:
#line 5907 "modelParser.y" /* yacc.c:1648  */
    {
	std::string str("exp");
	str += '(';
	str += (yyvsp[-1].p_ODE_String)->ode;
	str += ')';
	(yyvsp[-1].p_ODE_String)->ode = str;

	if(parseResult.bConstant)
	{
		(yyvsp[-1].p_ODE_String)->constant.exp_assign();
	}

	(yyval.p_ODE_String) = (yyvsp[-1].p_ODE_String);
}
#line 8411 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 292:
#line 5923 "modelParser.y" /* yacc.c:1648  */
    {
	std::string str("sin");
	str += '(';
	str += (yyvsp[-1].p_ODE_String)->ode;
	str += ')';
	(yyvsp[-1].p_ODE_String)->ode = str;

	if(parseResult.bConstant)
	{
		(yyvsp[-1].p_ODE_String)->constant.sin_assign();
	}

	(yyval.p_ODE_String) = (yyvsp[-1].p_ODE_String);
}
#line 8430 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 293:
#line 5939 "modelParser.y" /* yacc.c:1648  */
    {
	std::string str("cos");
	str += '(';
	str += (yyvsp[-1].p_ODE_String)->ode;
	str += ')';
	(yyvsp[-1].p_ODE_String)->ode = str;

	if(parseResult.bConstant)
	{
		(yyvsp[-1].p_ODE_String)->constant.cos_assign();
	}

	(yyval.p_ODE_String) = (yyvsp[-1].p_ODE_String);
}
#line 8449 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 294:
#line 5955 "modelParser.y" /* yacc.c:1648  */
    {
	std::string str("log");
	str += '(';
	str += (yyvsp[-1].p_ODE_String)->ode;
	str += ')';
	(yyvsp[-1].p_ODE_String)->ode = str;

	if(parseResult.bConstant)
	{
		(yyvsp[-1].p_ODE_String)->constant.log_assign();
	}

	(yyval.p_ODE_String) = (yyvsp[-1].p_ODE_String);
}
#line 8468 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 295:
#line 5971 "modelParser.y" /* yacc.c:1648  */
    {
	std::string str("sqrt");
	str += '(';
	str += (yyvsp[-1].p_ODE_String)->ode;
	str += ')';
	(yyvsp[-1].p_ODE_String)->ode = str;

	if(parseResult.bConstant)
	{
		(yyvsp[-1].p_ODE_String)->constant.sqrt_assign();
	}

	(yyval.p_ODE_String) = (yyvsp[-1].p_ODE_String);
}
#line 8487 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 296:
#line 5987 "modelParser.y" /* yacc.c:1648  */
    {
	(yyvsp[-2].p_ODE_String)->ode += '^';

	char strNum[NUM_LENGTH];
	sprintf(strNum, "%d", (int)(yyvsp[0].dblVal));
	std::string num(strNum);
	(yyvsp[-2].p_ODE_String)->ode += num;

	if(parseResult.bConstant)
	{
		(yyvsp[-2].p_ODE_String)->constant.pow_assign((int)(yyvsp[0].dblVal));
	}

	(yyval.p_ODE_String) = (yyvsp[-2].p_ODE_String);
}
#line 8507 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 297:
#line 6004 "modelParser.y" /* yacc.c:1648  */
    {
	std::string str;
	str += '-';
	str += (yyvsp[0].p_ODE_String)->ode;
	(yyvsp[0].p_ODE_String)->ode = str;

	if(parseResult.bConstant)
	{
		(yyvsp[0].p_ODE_String)->constant.inv_assign();
	}

	(yyval.p_ODE_String) = (yyvsp[0].p_ODE_String);
}
#line 8525 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 298:
#line 6019 "modelParser.y" /* yacc.c:1648  */
    {
	int id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));

	if(id < 0)
	{
		char errMsg[MSG_SIZE];

		sprintf(errMsg, "State variable %s is not declared TEST -- %d vars defined.", (*(yyvsp[0].identifier)).c_str(), continuousProblem.stateVarTab.size());
		parseError(errMsg, lineNum);
		exit(1);
	}

	flowstar::Interval intZero;
	parseResult.bConstant = false;
	parseResult.constant = intZero;

	(yyval.p_ODE_String) = new ODE_String(*(yyvsp[0].identifier), intZero);
}
#line 8548 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 299:
#line 6039 "modelParser.y" /* yacc.c:1648  */
    {
	char strNum[NUM_LENGTH];
	sprintf(strNum, "%.20e", ((yyvsp[-3].dblVal)+(yyvsp[-1].dblVal))/2);

	std::string num(strNum), strOde;

	strOde += '[';
	strOde += num;
	strOde += ' ';
	strOde += ',';
	strOde += ' ';
	strOde += num;
	strOde += ']';

	flowstar::Interval I((yyvsp[-3].dblVal), (yyvsp[-1].dblVal));
	(yyval.p_ODE_String) = new ODE_String(strOde, I);
}
#line 8570 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 300:
#line 6058 "modelParser.y" /* yacc.c:1648  */
    {
	char strNum[NUM_LENGTH];
	sprintf(strNum, "%.20e", (yyvsp[0].dblVal));
	std::string num(strNum), strOde;

	strOde += '[';
	strOde += num;
	strOde += ' ';
	strOde += ',';
	strOde += ' ';
	strOde += num;
	strOde += ']';

	flowstar::Interval I((yyvsp[0].dblVal));
	(yyval.p_ODE_String) = new ODE_String(strOde, I);
}
#line 8591 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 301:
#line 6197 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].p_LTI_Term)->stateVar_id >= 0)
	{
		dyn_A_row[0][(yyvsp[0].p_LTI_Term)->stateVar_id] += (yyvsp[0].p_LTI_Term)->coefficient;
	}
	else if((yyvsp[0].p_LTI_Term)->ti_par_id >= 0)
	{
		dyn_ti_row[0][(yyvsp[0].p_LTI_Term)->ti_par_id] += (yyvsp[0].p_LTI_Term)->coefficient;
	}
	else if((yyvsp[0].p_LTI_Term)->tv_par_id >= 0)
	{
		dyn_tv_row[0][(yyvsp[0].p_LTI_Term)->tv_par_id] += (yyvsp[0].p_LTI_Term)->coefficient;
	}
	else
	{
		dyn_B_row[0][0] += (yyvsp[0].p_LTI_Term)->coefficient;
	}
}
#line 8614 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 302:
#line 6217 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].p_LTI_Term)->stateVar_id >= 0)
	{
		dyn_A_row[0][(yyvsp[0].p_LTI_Term)->stateVar_id] -= (yyvsp[0].p_LTI_Term)->coefficient;
	}
	else if((yyvsp[0].p_LTI_Term)->ti_par_id >= 0)
	{
		dyn_ti_row[0][(yyvsp[0].p_LTI_Term)->ti_par_id] -= (yyvsp[0].p_LTI_Term)->coefficient;
	}
	else if((yyvsp[0].p_LTI_Term)->tv_par_id >= 0)
	{
		dyn_tv_row[0][(yyvsp[0].p_LTI_Term)->tv_par_id] -= (yyvsp[0].p_LTI_Term)->coefficient;
	}
	else
	{
		dyn_B_row[0][0] -= (yyvsp[0].p_LTI_Term)->coefficient;
	}
}
#line 8637 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 303:
#line 6237 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].p_LTI_Term)->stateVar_id >= 0)
	{
		dyn_A_row[0][(yyvsp[0].p_LTI_Term)->stateVar_id] -= (yyvsp[0].p_LTI_Term)->coefficient;
	}
	else if((yyvsp[0].p_LTI_Term)->ti_par_id >= 0)
	{
		dyn_ti_row[0][(yyvsp[0].p_LTI_Term)->ti_par_id] -= (yyvsp[0].p_LTI_Term)->coefficient;
	}
	else if((yyvsp[0].p_LTI_Term)->tv_par_id >= 0)
	{
		dyn_tv_row[0][(yyvsp[0].p_LTI_Term)->tv_par_id] -= (yyvsp[0].p_LTI_Term)->coefficient;
	}
	else
	{
		dyn_B_row[0][0] -= (yyvsp[0].p_LTI_Term)->coefficient;
	}
}
#line 8660 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 304:
#line 6257 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].p_LTI_Term)->stateVar_id >= 0)
	{
		dyn_A_row[0][(yyvsp[0].p_LTI_Term)->stateVar_id] = (yyvsp[0].p_LTI_Term)->coefficient;
	}
	else if((yyvsp[0].p_LTI_Term)->ti_par_id >= 0)
	{
		dyn_ti_row[0][(yyvsp[0].p_LTI_Term)->ti_par_id] = (yyvsp[0].p_LTI_Term)->coefficient;
	}
	else if((yyvsp[0].p_LTI_Term)->tv_par_id >= 0)
	{
		dyn_tv_row[0][(yyvsp[0].p_LTI_Term)->tv_par_id] = (yyvsp[0].p_LTI_Term)->coefficient;
	}
	else
	{
		dyn_B_row[0][0] = (yyvsp[0].p_LTI_Term)->coefficient;
	}
}
#line 8683 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 305:
#line 6279 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.p_LTI_Term) = new LTI_Term;

	flowstar::Interval coe((yyvsp[-2].dblVal));

	int id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));
	if(id >= 0)				// a state variable
	{
		(yyval.p_LTI_Term)->coefficient = coe;
		(yyval.p_LTI_Term)->stateVar_id = id;
	}
	else
	{
		id = continuousProblem.getIDForPar(*(yyvsp[0].identifier));
		if(id >= 0)			// a parameter
		{
			flowstar::Interval range;
			continuousProblem.getRangeForPar(range, *(yyvsp[0].identifier));
			(yyval.p_LTI_Term)->coefficient = coe * range;
		}
		else
		{
			id = continuousProblem.getIDForTIPar(*(yyvsp[0].identifier));
			if(id >= 0)		// a time-invariant uncertainty
			{
				(yyval.p_LTI_Term)->coefficient = coe;
				(yyval.p_LTI_Term)->ti_par_id = id;
			}
			else
			{
				id = continuousProblem.getIDForTVPar(*(yyvsp[0].identifier));
				if(id >= 0)	// a time-varying uncertainty
				{
					(yyval.p_LTI_Term)->coefficient = coe;
					(yyval.p_LTI_Term)->tv_par_id = id;
				}
				else		// not defined
				{
					char errMsg[MSG_SIZE];
					sprintf(errMsg, "Symbol %s is not defined.", (*(yyvsp[0].identifier)).c_str());
					parseError(errMsg, lineNum);
					exit(1);
				}
			}
		}
	}

	delete (yyvsp[0].identifier);
}
#line 8737 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 306:
#line 6330 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.p_LTI_Term) = new LTI_Term;

	flowstar::Interval coe((yyvsp[-5].dblVal), (yyvsp[-3].dblVal));

	int id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));
	if(id >= 0)				// a state variable
	{
		(yyval.p_LTI_Term)->coefficient = coe;
		(yyval.p_LTI_Term)->stateVar_id = id;
	}
	else
	{
		id = continuousProblem.getIDForPar(*(yyvsp[0].identifier));
		if(id >= 0)			// a parameter
		{
			flowstar::Interval range;
			continuousProblem.getRangeForPar(range, *(yyvsp[0].identifier));
			(yyval.p_LTI_Term)->coefficient = coe * range;
		}
		else
		{
			id = continuousProblem.getIDForTIPar(*(yyvsp[0].identifier));
			if(id >= 0)		// a time-invariant uncertainty
			{
				(yyval.p_LTI_Term)->coefficient = coe;
				(yyval.p_LTI_Term)->ti_par_id = id;
			}
			else
			{
				id = continuousProblem.getIDForTVPar(*(yyvsp[0].identifier));
				if(id >= 0)	// a time-varying uncertainty
				{
					(yyval.p_LTI_Term)->coefficient = coe;
					(yyval.p_LTI_Term)->tv_par_id = id;
				}
				else		// not defined
				{
					char errMsg[MSG_SIZE];
					sprintf(errMsg, "Symbol %s is not defined.", (*(yyvsp[0].identifier)).c_str());
					parseError(errMsg, lineNum);
					exit(1);
				}
			}
		}
	}

	delete (yyvsp[0].identifier);
}
#line 8791 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 307:
#line 6381 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.p_LTI_Term) = new LTI_Term;

	flowstar::Interval coe(1);

	int id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));
	if(id >= 0)				// a state variable
	{
		(yyval.p_LTI_Term)->coefficient = coe;
		(yyval.p_LTI_Term)->stateVar_id = id;
	}
	else
	{
		id = continuousProblem.getIDForPar(*(yyvsp[0].identifier));
		if(id >= 0)			// a parameter
		{
			flowstar::Interval range;
			continuousProblem.getRangeForPar(range, *(yyvsp[0].identifier));
			(yyval.p_LTI_Term)->coefficient = range;
		}
		else
		{
			id = continuousProblem.getIDForTIPar(*(yyvsp[0].identifier));
			if(id >= 0)		// a time-invariant uncertainty
			{
				(yyval.p_LTI_Term)->coefficient = coe;
				(yyval.p_LTI_Term)->ti_par_id = id;
			}
			else
			{
				id = continuousProblem.getIDForTVPar(*(yyvsp[0].identifier));
				if(id >= 0)	// a time-varying uncertainty
				{
					(yyval.p_LTI_Term)->coefficient = coe;
					(yyval.p_LTI_Term)->tv_par_id = id;
				}
				else		// not defined
				{
					char errMsg[MSG_SIZE];
					sprintf(errMsg, "Symbol %s is not defined.", (*(yyvsp[0].identifier)).c_str());
					parseError(errMsg, lineNum);
					exit(1);
				}
			}
		}
	}

	delete (yyvsp[0].identifier);
}
#line 8845 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 308:
#line 6432 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.p_LTI_Term) = new LTI_Term((yyvsp[-3].dblVal), (yyvsp[-1].dblVal), -1, -1, -1);
}
#line 8853 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 309:
#line 6437 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.p_LTI_Term) = new LTI_Term((yyvsp[0].dblVal), (yyvsp[0].dblVal), -1, -1, -1);
}
#line 8861 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 310:
#line 6453 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].p_LTI_Term)->stateVar_id >= 0)
	{
		dyn_A_row[0][(yyvsp[0].p_LTI_Term)->stateVar_id] += (yyvsp[0].p_LTI_Term)->coefficient;
	}
	else
	{
		dyn_B_row[0][0] += (yyvsp[0].p_LTI_Term)->coefficient;
	}
}
#line 8876 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 311:
#line 6465 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].p_LTI_Term)->stateVar_id >= 0)
	{
		dyn_A_row[0][(yyvsp[0].p_LTI_Term)->stateVar_id] -= (yyvsp[0].p_LTI_Term)->coefficient;
	}
	else
	{
		dyn_B_row[0][0] -= (yyvsp[0].p_LTI_Term)->coefficient;
	}
}
#line 8891 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 312:
#line 6477 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].p_LTI_Term)->stateVar_id >= 0)
	{
		dyn_A_row[0][(yyvsp[0].p_LTI_Term)->stateVar_id] -= (yyvsp[0].p_LTI_Term)->coefficient;
	}
	else
	{
		dyn_B_row[0][0] -= (yyvsp[0].p_LTI_Term)->coefficient;
	}
}
#line 8906 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 313:
#line 6489 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].p_LTI_Term)->stateVar_id >= 0)
	{
		dyn_A_row[0][(yyvsp[0].p_LTI_Term)->stateVar_id] = (yyvsp[0].p_LTI_Term)->coefficient;
	}
	else
	{
		dyn_B_row[0][0] = (yyvsp[0].p_LTI_Term)->coefficient;
	}
}
#line 8921 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 314:
#line 6503 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.p_LTI_Term) = new LTI_Term;

	flowstar::Interval coe((yyvsp[-2].dblVal));

	int id = hybridProblem.getIDForStateVar(*(yyvsp[0].identifier));
	if(id >= 0)				// a state variable
	{
		(yyval.p_LTI_Term)->coefficient = coe;
		(yyval.p_LTI_Term)->stateVar_id = id;
	}
	else
	{
		id = hybridProblem.getIDForPar(*(yyvsp[0].identifier));
		if(id >= 0)			// a parameter
		{
			flowstar::Interval range;
			hybridProblem.getRangeForPar(range, *(yyvsp[0].identifier));
			(yyval.p_LTI_Term)->coefficient = range;
		}
		else				// not defined
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "Symbol %s is not defined.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
	}

	delete (yyvsp[0].identifier);
}
#line 8957 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 315:
#line 6536 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.p_LTI_Term) = new LTI_Term;

	flowstar::Interval coe((yyvsp[-5].dblVal), (yyvsp[-3].dblVal));

	int id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));
	if(id >= 0)				// a state variable
	{
		(yyval.p_LTI_Term)->coefficient = coe;
		(yyval.p_LTI_Term)->stateVar_id = id;
	}
	else
	{
		id = hybridProblem.getIDForPar(*(yyvsp[0].identifier));
		if(id >= 0)			// a parameter
		{
			flowstar::Interval range;
			hybridProblem.getRangeForPar(range, *(yyvsp[0].identifier));
			(yyval.p_LTI_Term)->coefficient = range;
		}
		else				// not defined
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "Symbol %s is not defined.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
	}

	delete (yyvsp[0].identifier);
}
#line 8993 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 316:
#line 6569 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.p_LTI_Term) = new LTI_Term;

	flowstar::Interval coe(1);

	int id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));
	if(id >= 0)				// a state variable
	{
		(yyval.p_LTI_Term)->coefficient = coe;
		(yyval.p_LTI_Term)->stateVar_id = id;
	}
	else
	{
		id = hybridProblem.getIDForPar(*(yyvsp[0].identifier));
		if(id >= 0)			// a parameter
		{
			flowstar::Interval range;
			hybridProblem.getRangeForPar(range, *(yyvsp[0].identifier));
			(yyval.p_LTI_Term)->coefficient = range;
		}
		else				// not defined
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "Symbol %s is not defined.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
	}

	delete (yyvsp[0].identifier);
}
#line 9029 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 317:
#line 6602 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.p_LTI_Term) = new LTI_Term((yyvsp[-3].dblVal), (yyvsp[-1].dblVal), -1, -1, -1);
}
#line 9037 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 318:
#line 6607 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.p_LTI_Term) = new LTI_Term((yyvsp[0].dblVal), (yyvsp[0].dblVal), -1, -1, -1);
}
#line 9045 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 319:
#line 6637 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].p_LTV_Term)->stateVar_id >= 0)
	{
		dyn_A_t_row[0][(yyvsp[0].p_LTV_Term)->stateVar_id] += (yyvsp[0].p_LTV_Term)->coefficient;
	}
	else if((yyvsp[0].p_LTV_Term)->ti_par_id >= 0)
	{
		dyn_ti_t_row[0][(yyvsp[0].p_LTV_Term)->ti_par_id] += (yyvsp[0].p_LTV_Term)->coefficient;
	}
	else if((yyvsp[0].p_LTV_Term)->tv_par_id >= 0)
	{
		dyn_tv_t_row[0][(yyvsp[0].p_LTV_Term)->tv_par_id] += (yyvsp[0].p_LTV_Term)->coefficient;
	}
	else
	{
		dyn_B_t_row[0][0] += (yyvsp[0].p_LTV_Term)->coefficient;
	}
}
#line 9068 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 320:
#line 6657 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].p_LTV_Term)->stateVar_id >= 0)
	{
		dyn_A_t_row[0][(yyvsp[0].p_LTV_Term)->stateVar_id] -= (yyvsp[0].p_LTV_Term)->coefficient;
	}
	else if((yyvsp[0].p_LTV_Term)->ti_par_id >= 0)
	{
		dyn_ti_t_row[0][(yyvsp[0].p_LTV_Term)->ti_par_id] -= (yyvsp[0].p_LTV_Term)->coefficient;
	}
	else if((yyvsp[0].p_LTV_Term)->tv_par_id >= 0)
	{
		dyn_tv_t_row[0][(yyvsp[0].p_LTV_Term)->tv_par_id] -= (yyvsp[0].p_LTV_Term)->coefficient;
	}
	else
	{
		dyn_B_t_row[0][0] -= (yyvsp[0].p_LTV_Term)->coefficient;
	}
}
#line 9091 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 321:
#line 6677 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].p_LTV_Term)->stateVar_id >= 0)
	{
		dyn_A_t_row[0][(yyvsp[0].p_LTV_Term)->stateVar_id] -= (yyvsp[0].p_LTV_Term)->coefficient;
	}
	else if((yyvsp[0].p_LTV_Term)->ti_par_id >= 0)
	{
		dyn_ti_t_row[0][(yyvsp[0].p_LTV_Term)->ti_par_id] -= (yyvsp[0].p_LTV_Term)->coefficient;
	}
	else if((yyvsp[0].p_LTV_Term)->tv_par_id >= 0)
	{
		dyn_tv_t_row[0][(yyvsp[0].p_LTV_Term)->tv_par_id] -= (yyvsp[0].p_LTV_Term)->coefficient;
	}
	else
	{
		dyn_B_t_row[0][0] -= (yyvsp[0].p_LTV_Term)->coefficient;
	}
}
#line 9114 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 322:
#line 6697 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].p_LTV_Term)->stateVar_id >= 0)
	{
		dyn_A_t_row[0][(yyvsp[0].p_LTV_Term)->stateVar_id] = (yyvsp[0].p_LTV_Term)->coefficient;
	}
	else if((yyvsp[0].p_LTV_Term)->ti_par_id >= 0)
	{
		dyn_ti_t_row[0][(yyvsp[0].p_LTV_Term)->ti_par_id] = (yyvsp[0].p_LTV_Term)->coefficient;
	}
	else if((yyvsp[0].p_LTV_Term)->tv_par_id >= 0)
	{
		dyn_tv_t_row[0][(yyvsp[0].p_LTV_Term)->tv_par_id] = (yyvsp[0].p_LTV_Term)->coefficient;
	}
	else
	{
		dyn_B_t_row[0][0] = (yyvsp[0].p_LTV_Term)->coefficient;
	}
}
#line 9137 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 323:
#line 6720 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.p_LTV_Term) = new LTV_Term;

	int id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));
	if(id >= 0)				// a state variable
	{
		(yyval.p_LTV_Term)->coefficient = *(yyvsp[-3].pUpoly);
		(yyval.p_LTV_Term)->stateVar_id = id;
	}
	else
	{
		id = continuousProblem.getIDForPar(*(yyvsp[0].identifier));
		if(id >= 0)			// a parameter
		{
			flowstar::Interval range;
			continuousProblem.getRangeForPar(range, *(yyvsp[0].identifier));
			(yyval.p_LTV_Term)->coefficient = (*(yyvsp[-3].pUpoly)) * range;
		}
		else
		{
			id = continuousProblem.getIDForTIPar(*(yyvsp[0].identifier));
			if(id >= 0)		// a time-invariant uncertainty
			{
				(yyval.p_LTV_Term)->coefficient = *(yyvsp[-3].pUpoly);
				(yyval.p_LTV_Term)->ti_par_id = id;
			}
			else
			{
				id = continuousProblem.getIDForTVPar(*(yyvsp[0].identifier));
				if(id >= 0)	// a time-varying uncertainty
				{
					(yyval.p_LTV_Term)->coefficient = *(yyvsp[-3].pUpoly);
					(yyval.p_LTV_Term)->tv_par_id = id;
				}
				else		// not defined
				{
					char errMsg[MSG_SIZE];
					sprintf(errMsg, "Symbol %s is not defined.", (*(yyvsp[0].identifier)).c_str());
					parseError(errMsg, lineNum);
					exit(1);
				}
			}
		}
	}

	delete (yyvsp[-3].pUpoly);
	delete (yyvsp[0].identifier);
}
#line 9190 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 324:
#line 6770 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.p_LTV_Term) = new LTV_Term;
	flowstar::Interval intOne(1);

	int id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));
	if(id >= 0)				// a state variable
	{
		(yyval.p_LTV_Term)->coefficient = intOne;
		(yyval.p_LTV_Term)->stateVar_id = id;
	}
	else
	{
		id = continuousProblem.getIDForPar(*(yyvsp[0].identifier));
		if(id >= 0)			// a parameter
		{
			flowstar::Interval range;
			continuousProblem.getRangeForPar(range, *(yyvsp[0].identifier));
			(yyval.p_LTV_Term)->coefficient = range;
		}
		else
		{
			id = continuousProblem.getIDForTIPar(*(yyvsp[0].identifier));
			if(id >= 0)		// a time-invariant uncertainty
			{
				(yyval.p_LTV_Term)->coefficient = intOne;
				(yyval.p_LTV_Term)->ti_par_id = id;
			}
			else
			{
				id = continuousProblem.getIDForTVPar(*(yyvsp[0].identifier));
				if(id >= 0)	// a time-varying uncertainty
				{
					(yyval.p_LTV_Term)->coefficient = intOne;
					(yyval.p_LTV_Term)->tv_par_id = id;
				}
				else		// not defined
				{
					char errMsg[MSG_SIZE];
					sprintf(errMsg, "Symbol %s is not defined.", (*(yyvsp[0].identifier)).c_str());
					parseError(errMsg, lineNum);
					exit(1);
				}
			}
		}
	}

	delete (yyvsp[0].identifier);
}
#line 9243 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 325:
#line 6820 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.p_LTV_Term) = new LTV_Term(*(yyvsp[-1].pUpoly), -1, -1, -1);

	delete (yyvsp[-1].pUpoly);
}
#line 9253 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 326:
#line 6832 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].p_LTV_Term)->stateVar_id >= 0)
	{
		dyn_A_t_row[0][(yyvsp[0].p_LTV_Term)->stateVar_id] += (yyvsp[0].p_LTV_Term)->coefficient;
	}
	else
	{
		dyn_B_t_row[0][0] += (yyvsp[0].p_LTV_Term)->coefficient;
	}
}
#line 9268 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 327:
#line 6844 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].p_LTV_Term)->stateVar_id >= 0)
	{
		dyn_A_t_row[0][(yyvsp[0].p_LTV_Term)->stateVar_id] -= (yyvsp[0].p_LTV_Term)->coefficient;
	}
	else
	{
		dyn_B_t_row[0][0] -= (yyvsp[0].p_LTV_Term)->coefficient;
	}
}
#line 9283 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 328:
#line 6856 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].p_LTV_Term)->stateVar_id >= 0)
	{
		dyn_A_t_row[0][(yyvsp[0].p_LTV_Term)->stateVar_id] -= (yyvsp[0].p_LTV_Term)->coefficient;
	}
	else
	{
		dyn_B_t_row[0][0] -= (yyvsp[0].p_LTV_Term)->coefficient;
	}
}
#line 9298 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 329:
#line 6868 "modelParser.y" /* yacc.c:1648  */
    {
	if((yyvsp[0].p_LTV_Term)->stateVar_id >= 0)
	{
		dyn_A_t_row[0][(yyvsp[0].p_LTV_Term)->stateVar_id] = (yyvsp[0].p_LTV_Term)->coefficient;
	}
	else
	{
		dyn_B_t_row[0][0] = (yyvsp[0].p_LTV_Term)->coefficient;
	}
}
#line 9313 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 330:
#line 6884 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.p_LTV_Term) = new LTV_Term;

	int id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));
	if(id >= 0)				// a state variable
	{
		(yyval.p_LTV_Term)->coefficient = *(yyvsp[-3].pUpoly);
		(yyval.p_LTV_Term)->stateVar_id = id;
	}
	else
	{
		id = continuousProblem.getIDForPar(*(yyvsp[0].identifier));
		if(id >= 0)			// a parameter
		{
			flowstar::Interval range;
			continuousProblem.getRangeForPar(range, *(yyvsp[0].identifier));
			(yyval.p_LTV_Term)->coefficient = (*(yyvsp[-3].pUpoly)) * range;
		}
		else		// not defined
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "Symbol %s is not defined.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
	}

	delete (yyvsp[-3].pUpoly);
	delete (yyvsp[0].identifier);
}
#line 9348 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 331:
#line 6916 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.p_LTV_Term) = new LTV_Term;
	flowstar::Interval intOne(1);

	int id = continuousProblem.getIDForStateVar(*(yyvsp[0].identifier));
	if(id >= 0)				// a state variable
	{
		(yyval.p_LTV_Term)->coefficient = intOne;
		(yyval.p_LTV_Term)->stateVar_id = id;
	}
	else
	{
		id = continuousProblem.getIDForPar(*(yyvsp[0].identifier));
		if(id >= 0)			// a parameter
		{
			flowstar::Interval range;
			continuousProblem.getRangeForPar(range, *(yyvsp[0].identifier));
			(yyval.p_LTV_Term)->coefficient = range;
		}
		else		// not defined
		{
			char errMsg[MSG_SIZE];
			sprintf(errMsg, "Symbol %s is not defined.", (*(yyvsp[0].identifier)).c_str());
			parseError(errMsg, lineNum);
			exit(1);
		}
	}

	delete (yyvsp[0].identifier);
}
#line 9383 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 332:
#line 6948 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.p_LTV_Term) = new LTV_Term(*(yyvsp[-1].pUpoly), -1, -1, -1);

	delete (yyvsp[-1].pUpoly);
}
#line 9393 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 333:
#line 6963 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.pUpoly) = (yyvsp[-2].pUpoly);
	(*(yyval.pUpoly)) += (*(yyvsp[0].pUpoly));

	delete (yyvsp[0].pUpoly);
}
#line 9404 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 334:
#line 6971 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.pUpoly) = (yyvsp[-2].pUpoly);
	(*(yyval.pUpoly)) -= (*(yyvsp[0].pUpoly));

	delete (yyvsp[0].pUpoly);
}
#line 9415 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 335:
#line 6979 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.pUpoly) = (yyvsp[-1].pUpoly);
}
#line 9423 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 336:
#line 6984 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.pUpoly) = (yyvsp[-2].pUpoly);
	(*(yyval.pUpoly)) *= (*(yyvsp[0].pUpoly));

	delete (yyvsp[0].pUpoly);
}
#line 9434 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 337:
#line 6992 "modelParser.y" /* yacc.c:1648  */
    {
	int exp = (int) (yyvsp[0].dblVal);

	if(exp == 0)
	{
		(yyval.pUpoly) = new flowstar::UnivariatePolynomial(1);
	}
	else
	{
		(yyval.pUpoly) = new flowstar::UnivariatePolynomial;
		(*(yyvsp[-2].pUpoly)).pow(*(yyval.pUpoly), exp);
	}

	delete (yyvsp[-2].pUpoly);
}
#line 9454 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 338:
#line 7009 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Interval I(-1);
	(yyval.pUpoly) = (yyvsp[0].pUpoly);
	(*(yyval.pUpoly)) *= I;
}
#line 9464 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 339:
#line 7016 "modelParser.y" /* yacc.c:1648  */
    {
	std::string tVar("t");
	if((yyvsp[0].identifier)->compare(tVar) == 0)
	{
		(yyval.pUpoly) = new flowstar::UnivariatePolynomial(1, 1);
	}
	else
	{
		char errMsg[MSG_SIZE];
		sprintf(errMsg, "The time variable should be denoted by t.");
		parseError(errMsg, lineNum);
		exit(1);
	}
}
#line 9483 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 340:
#line 7032 "modelParser.y" /* yacc.c:1648  */
    {
	flowstar::Interval I((yyvsp[-3].dblVal), (yyvsp[-1].dblVal));
	(yyval.pUpoly) = new flowstar::UnivariatePolynomial(I);
}
#line 9492 "modelParser.tab.c" /* yacc.c:1648  */
    break;

  case 341:
#line 7038 "modelParser.y" /* yacc.c:1648  */
    {
	(yyval.pUpoly) = new flowstar::UnivariatePolynomial((yyvsp[0].dblVal));
}
#line 9500 "modelParser.tab.c" /* yacc.c:1648  */
    break;


#line 9504 "modelParser.tab.c" /* yacc.c:1648  */
      default: break;
    }
  /* User semantic actions sometimes alter yychar, and that requires
     that yytoken be updated with the new translation.  We take the
     approach of translating immediately before every use of yytoken.
     One alternative is translating here after every semantic action,
     but that translation would be missed if the semantic action invokes
     YYABORT, YYACCEPT, or YYERROR immediately after altering yychar or
     if it invokes YYBACKUP.  In the case of YYABORT or YYACCEPT, an
     incorrect destructor might then be invoked immediately.  In the
     case of YYERROR or YYBACKUP, subsequent parser actions might lead
     to an incorrect destructor call or verbose syntax error message
     before the lookahead is translated.  */
  YY_SYMBOL_PRINT ("-> $$ =", yyr1[yyn], &yyval, &yyloc);

  YYPOPSTACK (yylen);
  yylen = 0;
  YY_STACK_PRINT (yyss, yyssp);

  *++yyvsp = yyval;

  /* Now 'shift' the result of the reduction.  Determine what state
     that goes to, based on the state we popped back to and the rule
     number reduced by.  */

  yyn = yyr1[yyn];

  yystate = yypgoto[yyn - YYNTOKENS] + *yyssp;
  if (0 <= yystate && yystate <= YYLAST && yycheck[yystate] == *yyssp)
    yystate = yytable[yystate];
  else
    yystate = yydefgoto[yyn - YYNTOKENS];

  goto yynewstate;


/*--------------------------------------.
| yyerrlab -- here on detecting error.  |
`--------------------------------------*/
yyerrlab:
  /* Make sure we have latest lookahead translation.  See comments at
     user semantic actions for why this is necessary.  */
  yytoken = yychar == YYEMPTY ? YYEMPTY : YYTRANSLATE (yychar);

  /* If not already recovering from an error, report this error.  */
  if (!yyerrstatus)
    {
      ++yynerrs;
#if ! YYERROR_VERBOSE
      yyerror (YY_("syntax error"));
#else
# define YYSYNTAX_ERROR yysyntax_error (&yymsg_alloc, &yymsg, \
                                        yyssp, yytoken)
      {
        char const *yymsgp = YY_("syntax error");
        int yysyntax_error_status;
        yysyntax_error_status = YYSYNTAX_ERROR;
        if (yysyntax_error_status == 0)
          yymsgp = yymsg;
        else if (yysyntax_error_status == 1)
          {
            if (yymsg != yymsgbuf)
              YYSTACK_FREE (yymsg);
            yymsg = (char *) YYSTACK_ALLOC (yymsg_alloc);
            if (!yymsg)
              {
                yymsg = yymsgbuf;
                yymsg_alloc = sizeof yymsgbuf;
                yysyntax_error_status = 2;
              }
            else
              {
                yysyntax_error_status = YYSYNTAX_ERROR;
                yymsgp = yymsg;
              }
          }
        yyerror (yymsgp);
        if (yysyntax_error_status == 2)
          goto yyexhaustedlab;
      }
# undef YYSYNTAX_ERROR
#endif
    }



  if (yyerrstatus == 3)
    {
      /* If just tried and failed to reuse lookahead token after an
         error, discard it.  */

      if (yychar <= YYEOF)
        {
          /* Return failure if at end of input.  */
          if (yychar == YYEOF)
            YYABORT;
        }
      else
        {
          yydestruct ("Error: discarding",
                      yytoken, &yylval);
          yychar = YYEMPTY;
        }
    }

  /* Else will try to reuse lookahead token after shifting the error
     token.  */
  goto yyerrlab1;


/*---------------------------------------------------.
| yyerrorlab -- error raised explicitly by YYERROR.  |
`---------------------------------------------------*/
yyerrorlab:

  /* Pacify compilers like GCC when the user code never invokes
     YYERROR and the label yyerrorlab therefore never appears in user
     code.  */
  if (/*CONSTCOND*/ 0)
     goto yyerrorlab;

  /* Do not reclaim the symbols of the rule whose action triggered
     this YYERROR.  */
  YYPOPSTACK (yylen);
  yylen = 0;
  YY_STACK_PRINT (yyss, yyssp);
  yystate = *yyssp;
  goto yyerrlab1;


/*-------------------------------------------------------------.
| yyerrlab1 -- common code for both syntax error and YYERROR.  |
`-------------------------------------------------------------*/
yyerrlab1:
  yyerrstatus = 3;      /* Each real token shifted decrements this.  */

  for (;;)
    {
      yyn = yypact[yystate];
      if (!yypact_value_is_default (yyn))
        {
          yyn += YYTERROR;
          if (0 <= yyn && yyn <= YYLAST && yycheck[yyn] == YYTERROR)
            {
              yyn = yytable[yyn];
              if (0 < yyn)
                break;
            }
        }

      /* Pop the current state because it cannot handle the error token.  */
      if (yyssp == yyss)
        YYABORT;


      yydestruct ("Error: popping",
                  yystos[yystate], yyvsp);
      YYPOPSTACK (1);
      yystate = *yyssp;
      YY_STACK_PRINT (yyss, yyssp);
    }

  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  *++yyvsp = yylval;
  YY_IGNORE_MAYBE_UNINITIALIZED_END


  /* Shift the error token.  */
  YY_SYMBOL_PRINT ("Shifting", yystos[yyn], yyvsp, yylsp);

  yystate = yyn;
  goto yynewstate;


/*-------------------------------------.
| yyacceptlab -- YYACCEPT comes here.  |
`-------------------------------------*/
yyacceptlab:
  yyresult = 0;
  goto yyreturn;

/*-----------------------------------.
| yyabortlab -- YYABORT comes here.  |
`-----------------------------------*/
yyabortlab:
  yyresult = 1;
  goto yyreturn;

#if !defined yyoverflow || YYERROR_VERBOSE
/*-------------------------------------------------.
| yyexhaustedlab -- memory exhaustion comes here.  |
`-------------------------------------------------*/
yyexhaustedlab:
  yyerror (YY_("memory exhausted"));
  yyresult = 2;
  /* Fall through.  */
#endif

yyreturn:
  if (yychar != YYEMPTY)
    {
      /* Make sure we have latest lookahead translation.  See comments at
         user semantic actions for why this is necessary.  */
      yytoken = YYTRANSLATE (yychar);
      yydestruct ("Cleanup: discarding lookahead",
                  yytoken, &yylval);
    }
  /* Do not reclaim the symbols of the rule whose action triggered
     this YYABORT or YYACCEPT.  */
  YYPOPSTACK (yylen);
  YY_STACK_PRINT (yyss, yyssp);
  while (yyssp != yyss)
    {
      yydestruct ("Cleanup: popping",
                  yystos[*yyssp], yyvsp);
      YYPOPSTACK (1);
    }
#ifndef yyoverflow
  if (yyss != yyssa)
    YYSTACK_FREE (yyss);
#endif
#if YYERROR_VERBOSE
  if (yymsg != yymsgbuf)
    YYSTACK_FREE (yymsg);
#endif
  return yyresult;
}
#line 7056 "modelParser.y" /* yacc.c:1907  */


int yyerror(const char * what)
{
	fprintf(stderr, "Error line %d: %s\n", lineNum, what);
	err = true;
	return 1;
}

int yyerror(std::string what)
{
	std::cerr << "Error line "<< lineNum << " " << what << std::endl;
	err = true;
	return 1;
}
