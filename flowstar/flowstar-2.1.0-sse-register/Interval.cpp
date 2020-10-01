// cplusplusexperiments.cpp : This file contains the 'main' function. Program execution begins and ends there.
//

#include <stdexcept>
#include <sstream> //stringstream
#include <iomanip> //setprecision
#include <vector>
#include <fenv.h>
#pragma STDC FENV_ACCESS ON

#include "Interval.h"
#define RESTORE_ROUNDING_MODE false

using namespace flowstar;
mpfr_prec_t intervalNumPrecision = normal_precision;

int lastUsed = -1;
int origMode = -1;

bool coefficientOutputFormatSet = false;
char coefficientFormatCStr[6];

void setCoefficientFormatCStr() {
	char format[6];
	if (PN > 99) {
		//need to increase the size of char coefficientFormatCStr;
		throw std::runtime_error("output only supports precision <= 99");
	}
	sprintf(coefficientFormatCStr, "%%.%dg", PN);
	//cout << "'" << coefficientFormatCStr << "'" << endl;
}

namespace flowstar
{
	inline void setMode(int mode) {
		if (lastUsed != mode) {
			std::fesetround(mode);
			lastUsed = mode;
		}
	}

	inline void saveMode() {
#if RESTORE_ROUNDING_MODE
		origMode = std::fegetround();
#endif
	}

	inline void restoreMode() {
		// Restore the original rounding mode
#if RESTORE_ROUNDING_MODE
		if (lastUsed != origMode) {
			std::fesetround(origMode);
			lastUsed = origMode;
		}
#endif
	}
}

Real::Real()
{
	mpfr_init2(value, intervalNumPrecision);
	mpfr_set_ui(value, 0L, MPFR_RNDD);
}

Real::Real(const double v)
{
	mpfr_init2(value, intervalNumPrecision);
	mpfr_set_d(value, v, MPFR_RNDN);
}

Real::Real(const Real& real)
{
	mpfr_init2(value, intervalNumPrecision);
	mpfr_set(value, real.value, MPFR_RNDN);
}

Real::~Real()
{
	mpfr_clear(value);
}

bool Real::isZero() const
{
	return mpfr_cmp_ui(value, 0L);
}

double Real::getValue_RNDD() const
{
	return mpfr_get_d(value, MPFR_RNDD);
}

double Real::getValue_RNDU() const
{
	return mpfr_get_d(value, MPFR_RNDU);
}

void Real::abs(Real& real) const
{
	mpfr_abs(real.value, value, MPFR_RNDU);
}

void Real::abs_assign()
{
	mpfr_abs(value, value, MPFR_RNDU);
}

void Real::to_sym_int(Interval& I) const
{
	I.interval[1] = -getValue_RNDD();
	I.interval[0] = getValue_RNDU();
}

void Real::exp_RNDU(Real& result) const
{
	mpfr_exp(result.value, value, MPFR_RNDU);
}

void Real::exp_assign_RNDU()
{
	mpfr_exp(value, value, MPFR_RNDU);
}

void Real::pow_assign_RNDU(const int n)
{
	mpfr_pow_ui(value, value, n, MPFR_RNDU);
}

void Real::rec(Real& result) const
{
	mpfr_ui_div(result.value, 1L, value, MPFR_RNDN);
}

void Real::add_RNDD(Real& result, const Real& real) const
{
	mpfr_add(result.value, value, real.value, MPFR_RNDD);
}

void Real::add_assign_RNDD(const Real& real)
{
	mpfr_add(value, value, real.value, MPFR_RNDD);
}

void Real::add_RNDU(Real& result, const Real& real) const
{
	mpfr_add(result.value, value, real.value, MPFR_RNDU);
}

void Real::add_assign_RNDU(const Real& real)
{
	mpfr_add(value, value, real.value, MPFR_RNDU);
}

void Real::add_RNDN(Real& result, const Real& real) const
{
	mpfr_add(result.value, value, real.value, MPFR_RNDN);
}

void Real::add_assign_RNDN(const Real& real)
{
	mpfr_add(value, value, real.value, MPFR_RNDN);
}

void Real::sub_RNDD(Real& result, const Real& real) const
{
	mpfr_sub(result.value, value, real.value, MPFR_RNDD);
}

void Real::sub_assign_RNDD(const Real& real)
{
	mpfr_sub(value, value, real.value, MPFR_RNDD);
}

void Real::sub_RNDU(Real& result, const Real& real) const
{
	mpfr_sub(result.value, value, real.value, MPFR_RNDU);
}

void Real::sub_assign_RNDU(const Real& real)
{
	mpfr_sub(value, value, real.value, MPFR_RNDU);
}

void Real::mul_RNDD(Real& result, const Real& real) const
{
	mpfr_mul(result.value, value, real.value, MPFR_RNDD);
}

void Real::mul_assign_RNDD(const Real& real)
{
	mpfr_mul(value, value, real.value, MPFR_RNDD);
}

void Real::mul_RNDU(Real& result, const Real& real) const
{
	mpfr_mul(result.value, value, real.value, MPFR_RNDU);
}

void Real::mul_assign_RNDU(const Real& real)
{
	mpfr_mul(value, value, real.value, MPFR_RNDU);
}

void Real::mul_RNDD(Real& result, const int n) const
{
	mpfr_mul_si(result.value, value, n, MPFR_RNDD);
}

void Real::mul_assign_RNDD(const int n)
{
	mpfr_mul_si(value, value, n, MPFR_RNDD);
}

void Real::mul_RNDU(Real& result, const int n) const
{
	mpfr_mul_si(result.value, value, n, MPFR_RNDU);
}

void Real::mul_assign_RNDU(const int n)
{
	mpfr_mul_si(value, value, n, MPFR_RNDU);
}

void Real::div_RNDD(Real& result, const Real& real) const
{
	mpfr_div(result.value, value, real.value, MPFR_RNDD);
}

void Real::div_assign_RNDD(const Real& real)
{
	mpfr_div(value, value, real.value, MPFR_RNDD);
}

void Real::div_RNDU(Real& result, const Real& real) const
{
	mpfr_div(result.value, value, real.value, MPFR_RNDU);
}

void Real::div_assign_RNDU(const Real& real)
{
	mpfr_div(value, value, real.value, MPFR_RNDU);
}

void Real::div_RNDD(Real& result, const int n) const
{
	mpfr_div_si(result.value, value, n, MPFR_RNDD);
}

void Real::div_assign_RNDD(const int n)
{
	mpfr_div_si(value, value, n, MPFR_RNDD);
}

void Real::div_RNDU(Real& result, const int n) const
{
	mpfr_div_si(result.value, value, n, MPFR_RNDU);
}

void Real::div_assign_RNDU(const int n)
{
	mpfr_div_si(value, value, n, MPFR_RNDU);
}

void Real::output(FILE* fp) const
{
	mpfr_out_str(fp, 10, PN, value, MPFR_RNDN);
}

Real& Real::operator += (const Real& r)
{
	mpfr_add(value, value, r.value, MPFR_RNDN);
	return *this;
}

Real& Real::operator -= (const Real& r)
{
	mpfr_sub(value, value, r.value, MPFR_RNDN);
	return *this;
}

Real& Real::operator *= (const Real& r)
{
	mpfr_mul(value, value, r.value, MPFR_RNDN);
	return *this;
}

Real& Real::operator /= (const Real& r)
{
	mpfr_div(value, value, r.value, MPFR_RNDN);
	return *this;
}

Real& Real::operator += (const double d)
{
	mpfr_add_d(value, value, d, MPFR_RNDN);
	return *this;
}

Real& Real::operator -= (const double d)
{
	mpfr_sub_d(value, value, d, MPFR_RNDN);
	return *this;
}

Real& Real::operator *= (const double d)
{
	mpfr_mul_d(value, value, d, MPFR_RNDN);
	return *this;
}

Real& Real::operator /= (const double d)
{
	mpfr_div_d(value, value, d, MPFR_RNDN);
	return *this;
}

Real Real::operator + (const Real& r) const
{
	Real result = *this;
	result += r;
	return result;
}

Real Real::operator - (const Real& r) const
{
	Real result = *this;
	result -= r;
	return result;
}

Real Real::operator * (const Real& r) const
{
	Real result = *this;
	result *= r;
	return result;
}

Real Real::operator / (const Real& r) const
{
	Real result = *this;
	result /= r;
	return result;
}

bool Real::operator == (const Real& r) const
{
	if (mpfr_cmp(value, r.value) == 0)
	{
		return true;
	}
	else
	{
		return false;
	}
}

bool Real::operator != (const Real& r) const
{
	if (mpfr_cmp(value, r.value) == 0)
	{
		return false;
	}
	else
	{
		return true;
	}
}

bool Real::operator >= (const Real& r) const
{
	if (mpfr_cmp(value, r.value) >= 0)
	{
		return true;
	}
	else
	{
		return false;
	}
}

bool Real::operator > (const Real& r) const
{
	if (mpfr_cmp(value, r.value) > 0)
	{
		return true;
	}
	else
	{
		return false;
	}
}

Real& Real::operator = (const Real& r)
{
	if (this == &r)
		return *this;

	mpfr_set(value, r.value, MPFR_RNDN);
	return *this;
}

	Interval::Interval()
	{
		interval=_mm_setr_pd(0.0,-0.0);		
	}

	Interval::Interval(const double c)
	{
		interval=_mm_setr_pd(c,-c);
	}

	Interval::Interval(const double l, const double u)
	{
		interval=_mm_setr_pd(u,-l);
	}

	Interval::Interval(const char* strLo, const char* strUp)
	{
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		//lo = -std::stod(strLo);
		//setMode(FE_UPWARD);
		//up = std::stod(strUp);
		interval=_mm_setr_pd(std::stod(strUp),-std::stod(strLo));
		restoreMode();
	}

	Interval::Interval(const Interval& I)
	{
		interval=I.interval;
	}

    Interval::~Interval()
	{
	}

	void Interval::set (const double l, const double u)
	{
		interval=_mm_setr_pd(u,-l);
	}

	void Interval::set(const double c)
	{
		interval=_mm_setr_pd(c,-c);
	}

	void Interval::setInf(const double l)
	{
		interval[1]=-l;
	}

	void Interval::setInf(const Interval & I)
	{
		interval[1]=I.interval[1];
	}

	void Interval::setSup(const double u)
	{
		interval[0]=u;
	}

	void Interval::setSup(const Interval & S)
	{
		interval[0]= S.interval[0];
	}

	void Interval::split(Interval& left, Interval & right) const
	{
		saveMode();
		
		setMode(FE_UPWARD);
		left.interval=_mm_setr_pd((-interval[1] + interval[0]) / 2.0,interval[1]); // left.interval[0] is midpoint
		right.interval=_mm_setr_pd(interval[0],(interval[1] + -interval[0]) / 2.0); // right interval [1] is midpoint saved as -midpoint
		restoreMode();
	}

	void Interval::split(std::list<Interval>& result, const int n) const
	{
		throw std::runtime_error("'Interval::split(list<Interval> & result, const int n) const' not ported!");
	}

	void Interval::set_inf()
	{
		//lo=std::numeric_limits<double>::infinity();
		//up = std::numeric_limits<double>::infinity();; 
		// setting interval [-1,1] stored as (1,1)
		interval=_mm_setr_pd(1,1);
	}

	double Interval::sup() const
	{
		return interval[0];
	}

	double Interval::inf() const
	{
		return -interval[1];
	}

	void Interval::sup(Interval & S) const
	{
		S.interval=_mm_setr_pd(interval[0],-interval[0]);
	}

	void Interval::inf(Interval& I) const
	{
		I.interval=_mm_setr_pd(-interval[1],interval[1]);
	} // two functions with different names do the same thing...

	double Interval::midpoint() const
	{
		saveMode();
		setMode(FE_TONEAREST);
		return (-interval[1] + interval[0]) / 2.0;
		restoreMode();
		//unsure
	}

	void Interval::midpoint(Interval & M)const
	{
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		double mid= (-interval[1] + interval[0]) / 2.0;
		double minusmid=(interval[1] - interval[0]) / 2.0;
		M.interval=_mm_setr_pd(mid,minusmid);
		//setMode(FE_UPWARD);
		restoreMode();
		
	}

	void Interval::remove_midpoint(Interval & M)
	{
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		//setMode(FE_UPWARD);
		M.interval=_mm_setr_pd((-interval[1] + interval[0]) / 2.0,(interval[1] + -interval[0]) / 2.0);
		interval=_mm_add_pd(interval,_mm_shuffle_pd(M.interval,M.interval,1)); // sign change 
		restoreMode();
	}

	void Interval::remove_midpoint()
	{
		//double tmp1, tmp2;
		//same as before but saving temporary values into temp doubles instead of interval
		__m128d temp;
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		//setMode(FE_UPWARD);
		temp=_mm_setr_pd((interval[1] - interval[0]) / 2.0,(-interval[1] + interval[0]) / 2.0);
		//std::fesetround(FE_UPWARD);
		//setMode(FE_DOWNWARD);	
		interval=_mm_add_pd(interval,temp);
		restoreMode();
	}

	Interval Interval::intersect(const Interval & I) const //returning intersection of two intervals
	{
		Interval result;
		//flipping signs because of minus storing
		if(interval[1]<I.interval[1])
		{
			result.interval[1] = interval[1];
		}
		else
		{
			result.interval[1] = I.interval[1];
		}
		if (interval[0] > I.interval[0]) {
			result.interval[0] = I.interval[0];
		}
		else {
			result.interval[0] = interval[0];
		}

		return result;
	}

	void Interval::intersect_assign(const Interval & I) //assigning the intersection to left side interval
	{
		if(interval[1]>I.interval[1])
		{
			interval[1] = I.interval[1];
		}
		if(interval[0]>I.interval[0])
		{
			interval[0] = I.interval[0];
		}
	}

	void Interval::bloat (const double e)
	{
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);

		//setMode(FE_UPWARD);
		interval=_mm_add_pd(interval,_mm_set1_pd(e)); // _mm_set1_pd sets both registers to double e;
		restoreMode();
	}

	bool Interval::within(const Interval& I, const double e) const
	{
		double d;

		//TODO don't this is necessary, but leaving it here now

		saveMode();
		setMode(FE_UPWARD);
		__m128d intminusI=_mm_sub_pd(interval,I.interval);
		__m128d iminusInt=_mm_sub_pd(I.interval,interval);
		if (intminusI[0] >= 0) {
			//std::fesetround(FE_UPWARD);
			d = intminusI[0];
		}
		else {
			//std::fesetround(FE_DOWNWARD);
			//d = up - I.up;
			d = iminusInt[0];
		}

		//not needed now
		//std::fesetround(FE_UPWARD);
		//d = fabs(d);

		if (d > e) {
			return false;
		}

		if (iminusInt[1] <= 0) {
			//std::fesetround(FE_UPWARD);
			d =  intminusI[1];
		}
		else {
			//std::fesetround(FE_DOWNWARD);
			d = iminusInt[1];
		}

		//not needed now
		//setMode(FE_DOWNWARD);
		d = fabs(d);

		if (d > e) {
			return false;
		}
		restoreMode();

		return true;
	}

	double Interval::width() const
	{
		std::fesetround(FE_UPWARD);
		return interval[0] + interval[1];
	}

	void Interval::width(Interval& W) const
	{
		setMode(FE_UPWARD);
		W.interval=_mm_setr_pd(width(),-width());
		restoreMode();
	}

	double Interval::mag() const
	{
		//I assume that fabs will only change sign bit (no rounding needed)
		double inf = fabs(interval[1]);
		double sup = fabs(interval[0]);
		return inf < sup ? sup : inf;
		// no change needed here
	}

	void Interval::mag(Interval& M) const
	{
		//I assume that fabs will only change sign bit (no rounding needed)
		double tmp1 = fabs(interval[1]);
		double tmp2 = fabs(interval[0]);;

		if (tmp1 > tmp2) {
			M.interval=_mm_setr_pd(tmp1,-tmp1);
		}
		else {
			M.interval=_mm_setr_pd(tmp2,-tmp2);
		}
		//minuses added to lo limit saved into M
	}

	void Interval::abs(Interval& result) const
	{
		//I assume that fabs will only change sign bit (no rounding needed)
		double tmp1 = fabs(interval[1]);
		double tmp2 = fabs(interval[0]);

		if (tmp1 > tmp2) {
			result.interval=_mm_setr_pd(tmp1,-tmp2);
		}
		else {
			result.interval=_mm_setr_pd(tmp2,-tmp1);
		}
		//minuses added to lo limit saved into result
	}

	void Interval::abs_assign()
	{
		double tmp1 = fabs(interval[1]);
		double tmp2 = fabs(interval[0]);

		if (tmp1 > tmp2) {
			interval=_mm_setr_pd(tmp1,-tmp2);
		}
		else {
			interval=_mm_setr_pd(tmp2,-tmp1);
		}
		//minuses added to interval[1] limit assignments
	}

	bool Interval::subseteq(const Interval& I) const
	{
		//flipped signs because -interval[1]-s are compared
		if ((I.interval[1] >= interval[1]) && (I.interval[0] >= interval[0]))
			return true;
		return false;
	}

	bool Interval::supseteq(const Interval& I) const
	{
		//flipped signs because -lo-s are compared
		if ((interval[1] >= I.interval[1]) && (interval[0] >= I.interval[0]))
			return true;
		return false;
	}

	bool Interval::valid() const
	{
		if (interval[0] >= -interval[1]) {
			return true;
		}
		return false;
	}

	bool Interval::operator == (const Interval& I) const
	{
		return (interval[1] == I.interval[1]) && (interval[0] == I.interval[0]);
	}

	bool Interval::operator != (const Interval& I) const
	{
		return (interval[1] != I.interval[1]) || (interval[0] != I.interval[0]);
	}

	bool Interval::operator > (const Interval& I) const
	{
		return -interval[1] > I.interval[0];
	}

	bool Interval::operator < (const Interval& I) const
	{
		return interval[0] < -I.interval[1];
	}

	bool Interval::operator <= (const Interval& I) const
	{
		//why not <=?
		//return ( (mpfr_cmp(lo, I.lo) < 0) );
		//flipped signs
		return interval[1] > I.interval[1];
	}

	bool Interval::operator >= (const Interval& I) const
	{
		return interval[0] > I.interval[0];
	}

	bool Interval::smallereq(const Interval& I) const
	{
		return interval[0] <= -I.interval[1];
	}

	Interval& Interval::operator = (const Interval& I)
	{
		if (this == &I)
			return *this;	// check for self assignment

		interval=I.interval;

		return *this;
	}

	Interval& Interval::operator += (const Interval& I)
	{
		/*saveMode();
		if (lastUsed == FE_DOWNWARD) {
			std::fesetround(FE_UPWARD);
			lo += I.lo;
			up += I.up;
			lastUsed = FE_UPWARD;
		}
		else {
			if (lastUsed != FE_UPWARD) {
				std::fesetround(FE_UPWARD);
			}
			up += I.up;
			//std::fesetround(FE_DOWNWARD);
			lo += I.lo;
			//lastUsed = FE_DOWNWARD;
		}*/
		saveMode();
		setMode(FE_UPWARD);
		interval=_mm_add_pd(interval,I.interval);
		restoreMode();

		return *this;
	}

	Interval& Interval::operator -= (const Interval& I)
	{
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		//switched signs
	    interval=_mm_add_pd(interval,_mm_shuffle_pd(I.interval,I.interval,1)) ; // adding shuffled I so lo += I.up and up += I.lo
		restoreMode();
		return *this;
	}

	inline double Interval::mulMin(const Interval& I) const {
		//modified to return -min to be saved immediately to lo
		__m128d matchprod=_mm_mul_pd(_mm_mul_pd(interval,_mm_set1_pd(-1)),I.interval); 
		__m128d crossprod=_mm_mul_pd(interval,_mm_shuffle_pd(I.interval,I.interval,1));
		__m128d min=_mm_max_pd(matchprod,crossprod);
		return (min[0]>min[1])? min[0] : min[1];
		
	}

	inline double Interval::mulMax(const Interval& I) const {
	 
		__m128d matchprod=_mm_mul_pd(interval,I.interval);
		__m128d crossprod=_mm_mul_pd(_mm_mul_pd(interval,_mm_set1_pd(-1)),_mm_shuffle_pd(I.interval,I.interval,1)); 
		__m128d max=_mm_max_pd(matchprod,crossprod);

		return (max[0]>max[1])? max[0] : max[1];

	}
	

	Interval& Interval::operator *= (const Interval& I)
	{
		double min, max;
		saveMode();
		if (lastUsed == FE_DOWNWARD) {
			//std::fesetround(FE_DOWNWARD);// can skip this one
			setMode(FE_UPWARD);
			min = mulMin(I);
			//setMode(FE_UPWARD);
			max = mulMax(I);
			lastUsed = FE_UPWARD;
		}
		else {
			if (lastUsed != FE_UPWARD) { //can possibly skip this one
				setMode(FE_UPWARD);
			}
			max = mulMax(I);
			//setMode(FE_DOWNWARD);
			min = mulMin(I);
			//lastUsed = FE_DOWNWARD;
		}
		interval=_mm_setr_pd(max,min);
		restoreMode();

		return *this;
	}

	Interval& Interval::operator /= (const Interval& I)
	{
		Interval tmp;

		I.rec(tmp);
		*this *= tmp;

		return *this;
	}

	Interval& Interval::operator ++ ()
	{
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		interval[1]--; //sign switch here
		//setMode(FE_UPWARD);
		interval[0]++;
		restoreMode();

		return *this;
	}

	Interval& Interval::operator -- ()
	{
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		interval[1]++;
		//setMode(FE_UPWARD);
		interval[0]--;
		restoreMode();

		return *this;
	}

	const Interval Interval::operator + (const Interval& I) const
	{
		Interval result = *this;
		result += I;
		return result;
	}

	const Interval Interval::operator - (const Interval& I) const
	{
		Interval result = *this;
		result -= I;
		return result;
	}

	const Interval Interval::operator * (const Interval& I) const
	{
		Interval result = *this;
		result *= I;
		return result;
	}

	const Interval Interval::operator / (const Interval& I) const
	{
		Interval result = *this;
		result /= I;
		return result;
	}

	void Interval::sqrt(Interval& result) const
	{
		if (interval[1] > 0) { //flipping sign
			printf("Exception: Square root of a negative number.\n");
			exit(1);
		}
		saveMode();
		setMode(FE_DOWNWARD);
		result.interval[1] = -std::sqrt(-interval[1]);
		//setMode(FE_UPWARD);
		setMode(FE_UPWARD);
		result.interval[0] = std::sqrt(interval[0]);
		restoreMode();
	}

	void Interval::inv(Interval& result) const
	{
		//I assume that '-' will only change sign bit (no rounding needed)
		  //std::fesetround(FE_DOWNWARD);
		//std::fesetround(FE_UPWARD);
		result.interval=_mm_shuffle_pd(interval,interval,1);
	}

	void Interval::rec(Interval& result) const
	{
		saveMode();
		if (interval[1] >= 0 && interval[0] >= 0) {
			printf("Exception: Divided by 0.\n");
			exit(1);
		}
		else {
			//setMode(FE_DOWNWARD);
			setMode(FE_UPWARD);
			//result.lo = -1.0 / up;
			//result.up = -1.0 / lo;
			result.interval= _mm_div_pd(_mm_set1_pd(-1),_mm_shuffle_pd(interval,interval,1));
		}
		restoreMode();
	}

	void Interval::sqrt_assign()
	{
		saveMode();
		if (interval[1] > 0) {
			printf("Exception: Square root of a negative number.\n");
			exit(1);
		}
		setMode(FE_DOWNWARD);
		interval[1] = -std::sqrt(-interval[1]);
		//setMode(FE_UPWARD);
		setMode(FE_UPWARD);
		interval[0] = std::sqrt(interval[0]);
		restoreMode();
	}

	void Interval::inv_assign()
	{
		Interval result;
		this->inv(result);
		*this = result;
	}

	void Interval::rec_assign()
	{
		Interval result;
		this->rec(result);
		*this = result;
	}

	void Interval::add_assign(const double c)
	{
		saveMode();
		setMode(FE_UPWARD);
		//setMode(FE_DOWNWARD);
		//setMode(FE_UPWARD);	
		interval=_mm_add_pd(interval,_mm_setr_pd(c,-c));
		restoreMode();
	}

	void Interval::sub_assign(const double c)
	{
		saveMode();
		setMode(FE_UPWARD);
		//setMode(FE_DOWNWARD);
		//setMode(FE_UPWARD);
		interval=_mm_add_pd(interval,_mm_setr_pd(-c,c));
		restoreMode();
	}

	void Interval::mul_assign(const double c)
	{
		Interval result;

		saveMode();
		if (c > 0) {
			setMode(FE_UPWARD);
			//setMode(FE_DOWNWARD);
			//setMode(FE_UPWARD);
			result.interval=_mm_mul_pd(interval,_mm_set1_pd(c));
		}
		else {
			setMode(FE_UPWARD);
			//setMode(FE_DOWNWARD);
			//setMode(FE_UPWARD);
			result.interval=_mm_mul_pd(_mm_shuffle_pd(interval,interval,1),_mm_set1_pd(-c));
		}
		restoreMode();

		*this = result;
	}

	void Interval::div_assign(const double c)
	{
		Interval result;

		saveMode();
		if (c > 0) {
			setMode(FE_UPWARD);
			//setMode(FE_DOWNWARD);
			//setMode(FE_UPWARD);
			result.interval=_mm_div_pd(interval,_mm_set1_pd(c));
		}
		else {
			setMode(FE_UPWARD);
			//setMode(FE_DOWNWARD);
			//setMode(FE_UPWARD);
			result.interval=_mm_div_pd(_mm_shuffle_pd(interval,interval,1),_mm_set1_pd(-c));
		}
		restoreMode();

		*this = result;
	}

	Interval Interval::pow(const int n) const
	{
		Interval result;

		saveMode();
		setMode(FE_UPWARD);
		if (n % 2 == 1) {	// n is odd
			//setMode(FE_DOWNWARD);
			result.interval[1] = std::pow(interval[1], n); //low retains sign
			//setMode(FE_UPWARD);
			result.interval[0] = std::pow(interval[0], n);
			restoreMode();
			return result;
		}
		// n is even
		if (interval[1] <= 0) {			// 0 <= lo <= up signs flipped
			//setMode(FE_DOWNWARD);
			result.interval[1] = -std::pow(interval[1], n); //number def positive which means stores as def negative or 0
			//setMode(FE_UPWARD);
			result.interval[0] = std::pow(interval[0], n);
		}
		else if (interval[0] <= 0) {	// lo <= up <= 0
			//setMode(FE_DOWNWARD);
			result.interval[1] = -std::pow(interval[0], n); //number def positive which means stores as def negative or 0
			//setMode(FE_UPWARD);
			result.interval[0] = std::pow(interval[1], n);
		}
		else {									// lo < 0 < up
			double tmp1, tmp2;
			//setMode(FE_UPWARD);
			tmp1 = std::pow(interval[1], n);
			tmp2 = std::pow(interval[0], n);
			if (tmp1 >= tmp2) {
				result.interval[0] = tmp1;
			}
			else {
				result.interval[0] = tmp2;
			}
			//wasn't present in Flow* (but putting it here for being explicit)
			result.interval[1] = -0.0;
		}
		restoreMode();

		// return [a,b]
		return result;
	}

	Interval Interval::exp() const
	{
		Interval result;

		saveMode();
		throw std::runtime_error("std::exp function is not precise");
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		result.interval[1] = -std::exp(-interval[1]);
		//setMode(FE_UPWARD);
		result.interval[0] = std::exp(interval[0]);
		restoreMode();

		return result;
	}

	Interval Interval::sin() const
	{
	__m128d pi;
	__m128d tmp;
	saveMode();
	//setMode(FE_DOWNWARD);
	setMode(FE_UPWARD);
	//pi_lo is flipped because of rounding
	pi=_mm_setr_pd(-std::stod(str_pi_lo),std::stod(str_pi_up)); //switched order to skip a shuffle
	
	tmp=_mm_div_pd(interval,_mm_mul_pd(pi,_mm_setr_pd(-0.5,0.5)));
	//setMode(FE_DOWNWARD);
	
	tmp[0]=floor(tmp[0]);
	tmp[1]=ceil(tmp[1]);
	

	//setMode(FE_TONEAREST); //is that necessary

	int iUp= (int) tmp[0];
	int iLo= (int) tmp[1]; //flipped because lo is used to created
	
	int iPeriod= iUp + iLo; //sign flipped
	
	if(iPeriod >= 4)
	{
		Interval result(-1,1);
		return result;
	}
	else
	{
		int modUp = iUp % 4;
		if(modUp < 0)
			modUp += 4;

		int modLo = -iLo % 4; //iLo flipped to -iLo
		if(modLo < 0)
			modLo += 4;

		Interval result;
		double tmp1=0;
		double tmp2=0;
		

		switch(modLo)
		{
		case 0:
			switch(modUp)
			{
			case 0:
				if(iPeriod == 0)
				{
					//setMode(FE_DOWNWARD);
					result.interval[1]=::sin(interval[1]); //note that sin(x)=-sin(-x), since lo=-lo and we want to save -sin(x) there is no need to switch signs
					//setMode(FE_UPWARD); // upward rounding is still set
					result.interval[0]=::sin(interval[0]);
				}
				else
				{
					 //changed -1 to 1
					result.interval=_mm_set1_pd(1);
					//don't think rounding modes are necessary here;
				}
				break;
			case 1:
			    result.interval[0]=1;
                //setMode(FE_DOWNWARD);
				tmp1=::sin(interval[1]);
				tmp2=-::sin(interval[0]); //sign flipped using -tmp1 and -tmp2
				 //sign flip
				result.interval[1]= (tmp1<tmp2) ? tmp2 : tmp1;
				break;
			case 2:
			    result.interval[0]=1;
				//setMode(FE_DOWNWARD);
				result.interval[1]=::sin(-interval[0]); //minus added to up
				break;
			case 3:
			 //changed -1 to 1
				result.interval=_mm_set1_pd(1);
				break;
			}
			break;
		case 1:
			switch(modUp)
			{
			case 0:
			    result.interval[1]=1; //changed -1 to 1
				//setMode(FE_UPWARD);
				tmp1=::sin(-interval[1]); //needs to negate lo
				tmp2=::sin(interval[0]);
				result.interval[0]= (tmp1 >tmp2) ? tmp1 : tmp2;
				break;
			case 1:
				if(iPeriod == 0)
				{
					//setMode(FE_DOWNWARD);
					result.interval[1]=::sin(-interval[0]);
					//setMode(FE_UPWARD);
					result.interval[0]=::sin(-interval[1]);
				}
				else
				{
					 //changed -1 to 1
					result.interval=_mm_set1_pd(1);
				}
				break;
			case 2:
			    //setMode(FE_DOWNWARD);
				result.interval[1]=::sin(-interval[0]);
				//setMode(FE_UPWARD);
				result.interval[0]=::sin(-interval[1]);
				break;
			case 3:
				result.interval[1]=1;
				//setMode(FE_UPWARD);
				result.interval[0]=::sin(-interval[1]);
				break;
			}
			break;
		case 2:
			switch(modUp)
			{
			case 0:
				result.interval[1]=1;
				//setMode(FE_UPWARD);
				result.interval[0]=::sin(interval[0]);
				break;
			case 1:
				result.interval=_mm_set1_pd(1);
				break;
			case 2:
				if(iPeriod == 0)
				{
					//setMode(FE_DOWNWARD);
					result.interval[1]=::sin(-interval[0]);
					//setMode(FE_UPWARD);
					result.interval[0]=::sin(-interval[1]);
				}
				else
				{
					result.interval=_mm_set1_pd(1);
				}
				break;
			case 3:
				result.interval[1]=1;
				//setMode(FE_UPWARD);
				tmp1=::sin(-interval[1]);
				tmp2=::sin(interval[0]);
				result.interval[0]= (tmp1 > tmp2) ? tmp1 : tmp2;
				break;
			}
			break;
		case 3:
			switch(modUp)
			{
			case 0:
			    //setMode(FE_DOWNWARD);
				result.interval[1]=::sin(interval[1]);
				//setMode(FE_UPWARD);
				result.interval[0]=::sin(interval[0]);
				break;
			case 1:
			    //setMode(FE_DOWNWARD);
				result.interval[1]=::sin(interval[1]);
				result.interval[0]=1;
				break;
			case 2:
			    result.interval[0]=1;
				//setMode(FE_DOWNWARD);
				tmp1=::sin(interval[1]);
				tmp2=::sin(-interval[0]);
				result.interval[1]= (tmp1 < tmp2) ? tmp2 : tmp1;
				break;
			case 3:
				if(iPeriod == 0)
				{
					//setMode(FE_DOWNWARD);
					result.interval[1]=::sin(interval[1]);
					//setMode(FE_UPWARD);
					result.interval[0]=::sin(interval[0]);
				}
				else
				{
					result.interval=_mm_set1_pd(1);
				}
				break;
			}
			break;
		}
		restoreMode();

		return result;
	}
		//throw std::runtime_error("'Interval::sin() not ported!");
	}

	Interval Interval::cos() const
	{
	double pi_down;
	double pi_up;
	setMode(FE_UPWARD);
	pi_up=-std::stod(str_pi_up);
	pi_down=-std::stod("-"+std::string(str_pi_lo));
	pi_up/=2;
	pi_down/=2;
	pi_up+=interval[1];
	pi_down+=interval[0];
	Interval shift=Interval(-pi_up,pi_down);
	return shift.sin();
		//throw std::runtime_error("'Interval::cos() not ported!");
	}

	Interval Interval::log() const
	{
		if (interval[1] >= 0) { //flipped sign
			printf("Exception: Logarithm of a non-positive number.\n");
			exit(1);
		}
		else {
			Interval result;

			saveMode();
			throw std::runtime_error("std::exp function is not precise (after 17 digits");
			//setMode(FE_DOWNWARD);
			setMode(FE_UPWARD);
			result.interval[1] = -std::log(-interval[1]);
			//setMode(FE_UPWARD);
			result.interval[0] = std::log(interval[0]);
			restoreMode();

			return result;
		}
	}

	void Interval::pow_assign(const int n)
	{
		saveMode();
		setMode(FE_UPWARD);
		if (n % 2 == 1)		// n is odd
		{
			//setMode(FE_DOWNWARD);
			interval[1] = std::pow(interval[1], n);
			//setMode(FE_UPWARD);
			interval[0] = std::pow(interval[0], n);
			restoreMode();
			return;
		}
		// n is even
		if (interval[1] <= 0) {		// 0 <= lo <= up flipped sign
			//setMode(FE_DOWNWARD);
			interval[1] = -std::pow(interval[1], n-1)*interval[1];
			//setMode(FE_UPWARD);
			interval[0] = std::pow(interval[0], n);
		}
		else if (interval[0] <= 0) {		// lo <= up <= 0
			//setMode(FE_DOWNWARD);
			double tmp = -std::pow(interval[0], n-1)*interval[0];
			//setMode(FE_UPWARD);
			interval[0] = std::pow(interval[1], n);
			interval[1] = tmp;
		}
		else {							// lo < 0 < up
			double tmp1, tmp2;
			//setMode(FE_UPWARD);
			tmp1 = std::pow(interval[1], n);
			tmp2 = std::pow(interval[0], n);
			if (tmp1 >= tmp2) {
				interval[0] = tmp1;
			}
			else {
				interval[0] = tmp2;
			}
			interval[1] = -0.0;
		}
		restoreMode();
	}

	void Interval::exp_assign()
	{
		saveMode();
		throw std::runtime_error("std::exp function is not precise");
		setMode(FE_UPWARD);
		//setMode(FE_DOWNWARD);
		interval[1] = -std::exp(-interval[1]);
		//setMode(FE_UPWARD);
		interval[0] = std::exp(interval[0]);
		restoreMode();
	}

	void Interval::sin_assign()
	{
		*this = this->sin();
	}

	void Interval::cos_assign()
	{
		*this = this->cos();
	}

	void Interval::log_assign()
	{
		if (interval[1] >= 0) {
			printf("Exception: Logarithm of a non-positive number.\n");
			exit(1);
		}
		else {
			throw std::runtime_error("std::exp function is not precise (after 17 digits");
			saveMode();
			//setMode(FE_DOWNWARD);
			setMode(FE_UPWARD);
			interval[1] = -std::log(-interval[1]);
			//setMode(FE_UPWARD);
			interval[0] = std::log(interval[0]);
			restoreMode();
		}
	}

	double Interval::widthRatio(const Interval& I) const
	{
		double width1, width2, ratio;

		saveMode();
		setMode(FE_UPWARD);
		width1 = width();
		width2 = I.width(); //switched - to +

		ratio = width2 / width1;		// we assume that width1 >= width2
		restoreMode();

		return ratio;
	}

	void Interval::toString(std::string& result) const
	{
		//mlog1("(string) version");
		char strTemp[30];
		saveMode();

		std::string strInt;
		strInt += '[';

		//std::fesetround(FE_DOWNWARD);
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		sprintf(strTemp, "%.10e", interval[1]);
		std::string strLo(strTemp);
		if(strLo[0]=='-')
		{
			strLo = strLo.substr(1, strLo.length()-1); //cutting of wrong minus sign
		}
		else{ strLo = "-" + strLo; }
		
		strInt += strLo;
		strInt += ' ';
		strInt += ',';
		strInt += ' ';

		//std::fesetround(FE_UPWARD);
		//setMode(FE_UPWARD);
		sprintf(strTemp, "%.10e", interval[0]);
		std::string strUp(strTemp);
		strInt += strUp;
		strInt += ']';
		restoreMode();

		result = strInt;
	}

	void Interval::dump(FILE* fp) const
	{
		saveMode();
		if (coefficientOutputFormatSet == false) {
			setCoefficientFormatCStr();
		}
		fprintf(fp, "[");

		//15 is PN in Flow* (but it's arbitrary anyway)
	  //std::fesetround(FE_DOWNWARD);
		setMode(FE_TONEAREST);
		fprintf(fp, coefficientFormatCStr, -interval[1]);
		fprintf(fp, " , ");
		//std::fesetround(FE_UPWARD);
		//setMode(FE_TONEAREST);
		fprintf(fp, coefficientFormatCStr, interval[0]);

		fprintf(fp, "]");
		restoreMode();
	}

	void Interval::output(FILE* fp, const char* msg, const char* msg2) const
	{
		if (coefficientOutputFormatSet == false) {
			setCoefficientFormatCStr();
		}
		fprintf(fp, "%s [ ", msg);

		//15 is PN in Flow* (but it's arbitrary anyway)
	  //std::fesetround(FE_DOWNWARD);
		setMode(FE_TONEAREST);
		fprintf(fp, coefficientFormatCStr, -interval[1]);
		fprintf(fp, " , ");
		//std::fesetround(FE_UPWARD);
		  //setMode(FE_TONEAREST);
		fprintf(fp, coefficientFormatCStr, interval[0]);

		fprintf(fp, " ] %s", msg2);
		saveMode();
	}

	bool subseteq(const std::vector<Interval>& v1, const std::vector<Interval>& v2) {
		if (v1.size() != v2.size())
			throw std::invalid_argument("Different domains of vectors");
		for (int i = 0; i < v1.size(); i++) {
			if (v1[i].subseteq(v2[i]) == false) {
				return false;
			}
		}
		return true;
	}

	Interval::Interval(const Real& r)
	{
		Real temp = Real();
		temp-=r; //temp for the rounding
		interval=_mm_setr_pd(r.getValue_RNDU(),temp.getValue_RNDU());
	}

	Interval::Interval(const Real& c, const Real& r)
	{
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		Real temp = Real();
		temp-=c;
		 //changed RNDD, not sure about that
		//setMode(FE_UPWARD);
		interval=_mm_setr_pd(c.getValue_RNDU() + r.getValue_RNDU(),temp.getValue_RNDU() + r.getValue_RNDU());
		restoreMode();
	}

	Interval::Interval(const Real& l, const Real& u, const int n) //why const int n
	{
		Real temp = Real();
		temp-=l;
		interval=_mm_setr_pd(u.getValue_RNDU(),temp.getValue_RNDU());
	}

	bool Interval::isZero() const
	{
		Interval intZero;

		if (this->subseteq(intZero))
		{
			return true;
		}
		else
		{
			return false;
		}
	}

	void Interval::set(const Real& r)
	{
		Real temp = Real();
		temp-=r;
		interval=_mm_setr_pd(r.getValue_RNDU(),temp.getValue_RNDU());
	}

	void Interval::sup(Real& u) const
	{
		mpfr_set_d(u.value, interval[0], MPFR_RNDU);
	}

	void Interval::inf(Real& l) const
	{
		//Real temp=Real();
		//temp-=l;
		//mpfr_set_d(temp.value, lo, MPFR_RNDU);
		mpfr_set_d(l.value,-interval[1],MPFR_RNDD);
		//l.mul_assign_RNDU(-1);
		
	}

	void Interval::midpoint(Real& mid) const
	{
		saveMode();
		setMode(FE_TONEAREST);
		mpfr_set_d(mid.value, (-interval[1] + interval[0]) / 2.0, MPFR_RNDN);
		restoreMode();
	} //Not sure how to switch

	void Interval::toCenterForm(Real& center, Real& radius) const
	{
		saveMode();
		setMode(FE_TONEAREST);
		mpfr_set_d(center.value, (-interval[1] + interval[0]) / 2.0, MPFR_RNDN);

		setMode(FE_UPWARD);
		mpfr_set_d(radius.value, (interval[0] + interval[1]) / 2.0, MPFR_RNDU);
		restoreMode();
	} //Not sure how to switch

	void Interval::bloat(const Real& e)
	{
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		interval= _mm_add_pd(interval,_mm_set1_pd(e.getValue_RNDU()));
		restoreMode();
	} //have to double check

	void Interval::mag(Real& m) const
	{
		double tmp1 = fabs(interval[1]), tmp2 = fabs(interval[0]);

		if (tmp1 >= tmp2) {
			mpfr_set_d(m.value, tmp1, MPFR_RNDN);
			return;
		}
		mpfr_set_d(m.value, tmp2, MPFR_RNDN);
	}

	Interval& Interval::operator = (const Real& r)
	{
		Real temp = Real();
		temp-=r;
		interval= _mm_setr_pd(r.getValue_RNDU(),temp.getValue_RNDU());

		return *this;
	}

	Interval& Interval::operator = (const double d)
	{
		interval=_mm_setr_pd(d,-d);

		return *this;
	}

	Interval& Interval::operator += (const double c)
	{
		saveMode();
		setMode(FE_UPWARD);
		//setMode(FE_DOWNWARD);
		//setMode(FE_UPWARD);
		interval=_mm_add_pd(interval,_mm_setr_pd(c,-c));
		restoreMode();

		return *this;
	}

	Interval& Interval::operator -= (const double c)
	{
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		//setMode(FE_UPWARD);
		interval=_mm_add_pd(interval,_mm_setr_pd(-c,c)); // reverse addition
		restoreMode();

		return *this;
	}

	Interval& Interval::operator *= (const double c)
	{
		saveMode();
		setMode(FE_UPWARD);
		if (c >= 0) {
			//setMode(FE_DOWNWARD);
			//setMode(FE_UPWARD);
			interval=_mm_mul_pd(interval,_mm_set1_pd(c));
		}
		else {
			//setMode(FE_DOWNWARD);
			//setMode(FE_UPWARD);
			interval=_mm_mul_pd(_mm_shuffle_pd(interval,interval,1),_mm_set1_pd(-c));
		}
		restoreMode();

		return *this;
	}

	Interval& Interval::operator /= (const double c)
	{
		saveMode();
		setMode(FE_UPWARD);
		if (c >= 0) {
			//setMode(FE_DOWNWARD);
			//setMode(FE_UPWARD);
			interval=_mm_div_pd(interval,_mm_set1_pd(c));
		}
		else {
			//setMode(FE_DOWNWARD);
			//setMode(FE_UPWARD);
			interval=_mm_div_pd(_mm_shuffle_pd(interval,interval,1),_mm_set1_pd(-c));
		}
		restoreMode();

		return *this;
	}

	const Interval Interval::operator + (const double c) const
	{
		Interval result = *this;
		result += c;
		return result;
	}






	const Interval Interval::operator - (const double c) const
	{
		Interval result = *this;
		result -= c;
		return result;
	}
	const Interval Interval::operator * (const double c) const
	{
		Interval result;

		saveMode();
		setMode(FE_UPWARD);
		if (c > 0) {
			//setMode(FE_DOWNWARD);
			
			//setMode(FE_UPWARD);
			result.interval= _mm_mul_pd(interval,_mm_set1_pd(c));
		}
		else {
			//setMode(FE_DOWNWARD);
			//setMode(FE_UPWARD);
			result.interval=_mm_mul_pd(_mm_shuffle_pd(interval,interval,1),_mm_set1_pd(-c));
		}
		restoreMode();

		return result;
	}
	const Interval Interval::operator / (const double c) const
	{
		Interval result;

		saveMode();
		setMode(FE_UPWARD);
		if (c > 0) {
			//setMode(FE_DOWNWARD);
			//setMode(FE_UPWARD);
			result.interval= _mm_div_pd(interval,_mm_set1_pd(c));
		}
		else {
			//setMode(FE_DOWNWARD);
			//setMode(FE_UPWARD);
			result.interval=_mm_div_pd(_mm_shuffle_pd(interval,interval,1),_mm_set1_pd(c));
		}
		restoreMode();

		return result;
	}

	
	void Interval::mul_add(Interval* result, const Interval* intVec, const int size)
	{
		__m128d tmp;
		__m128d tmp2;

		saveMode();
		setMode(FE_UPWARD);
		if (interval[1] <= 0) //comparing flip
		{
			
			for (int i = 0; i < size; ++i)
			{
				if (intVec[i].interval[1]<= 0) //comparing flip
				{
					
					//setMode(FE_DOWNWARD);					
					//setMode(FE_UPWARD);
					tmp=_mm_mul_pd(interval,_mm_mul_pd(intVec[i].interval,_mm_setr_pd(1,-1)));
				}
				else if (intVec[i].interval[0] <= 0)
				{
					//setMode(FE_DOWNWARD);					
					//setMode(FE_UPWARD);
					tmp=_mm_mul_pd(_mm_shuffle_pd(interval,interval,1),_mm_mul_pd(intVec[i].interval,_mm_setr_pd(-1,1)));
				}
				else
				{
					//setMode(FE_DOWNWARD);					
					//setMode(FE_UPWARD);
					tmp=_mm_mul_pd(_mm_set1_pd(interval[0]),intVec[i].interval);
				}

				//setMode(FE_DOWNWARD);				
				//setMode(FE_UPWARD);
				result[i].interval=_mm_add_pd(result[i].interval,tmp);
			}
		}
		else if (interval[0] <= 0)
		{
			for (int i = 0; i < size; ++i)
			{
				if (intVec[i].interval[1] <= 0) //comparing flip
				{
					//setMode(FE_DOWNWARD);					
					//setMode(FE_UPWARD);
					tmp=_mm_mul_pd(interval,_mm_mul_pd(_mm_shuffle_pd(intVec[i].interval,intVec[i].interval,1),_mm_setr_pd(-1,1)));
				}
				else if (intVec[i].interval[0] <= 0)
				{
					//setMode(FE_DOWNWARD);
					//setMode(FE_UPWARD);
					tmp=_mm_mul_pd(_mm_shuffle_pd(interval,interval,1),_mm_mul_pd(_mm_shuffle_pd(intVec[i].interval,intVec[i].interval,1),_mm_setr_pd(1,-1)));
				}
				else
				{
					//setMode(FE_DOWNWARD);
					//setMode(FE_UPWARD);
					tmp= _mm_mul_pd(_mm_set1_pd(interval[1]),intVec[i].interval);
				}
				//setMode(FE_DOWNWARD);
				//setMode(FE_UPWARD);
				result[i].interval=_mm_add_pd(result[i].interval,tmp);
			}
		}
		else
		{
			for (int i = 0; i < size; ++i)
			{
				if (intVec[i].interval[1] >= 0)
				{
					//setMode(FE_DOWNWARD);
					//setMode(FE_UPWARD);
					tmp= _mm_mul_pd(interval,_mm_set1_pd(intVec[i].interval[0]));
				}
				else if (intVec[i].interval[0] <= 0)
				{
					//setMode(FE_DOWNWARD);
					//setMode(FE_UPWARD);
					tmp=_mm_mul_pd(_mm_shuffle_pd(interval,interval,1),_mm_set1_pd(intVec[i].interval[1]));
				}
				else
				{
					//setMode(FE_DOWNWARD);				
					tmp2=_mm_mul_pd(interval,_mm_shuffle_pd(intVec[i].interval,intVec[i].interval,1)); // tmp2 (tmp2,tmp1)

					if (tmp2[1] < tmp2[0]) // flipped sign
					{
						tmp[1] = tmp2[0];
					}
					else
					{
						tmp[1] = tmp2[1];
					}

					//setMode(FE_UPWARD);
					tmp2=_mm_mul_pd(interval,intVec[i].interval);

					if (tmp2[1] > tmp2[0])
					{
						tmp[0] = tmp2[1];
					}
					else
					{
						tmp[0] = tmp2[0];
					}
				}

				//setMode(FE_DOWNWARD);
				//setMode(FE_UPWARD);
				result[i].interval=_mm_add_pd(result[i].interval,tmp);
			}
		}
		restoreMode();
	}







	
	




// Run program: Ctrl + F5 or Debug > Start Without Debugging menu
// Debug program: F5 or Debug > Start Debugging menu

// Tips for Getting Started: 
//   1. Use the Solution Explorer window to add/manage files
//   2. Use the Team Explorer window to connect to source control
//   3. Use the Output window to see build output and other messages
//   4. Use the Error List window to view errors
//   5. Go to Project > Add New Item to create new code files, or Project > Add Existing Item to add existing code files to the project
//   6. In the future, to open this project again, go to File > Open > Project and select the .sln file
