/*---
  Flow*: A Verification Tool for Cyber-Physical Systems.
  Authors: Xin Chen, Sriram Sankaranarayanan, and Erika Abraham.
  Email: Xin Chen <chenxin415@gmail.com> if you have questions or comments.

	Modified: Kristjan Liiva (kristjan.liiva1@gmail.com)

  The code is released as is under the GNU General Public License (GPL).
---*/

/*
 * MPFR_RNDU: round toward plus infinity (roundTowardPositive in IEEE 754-2008),
 * MPFR_RNDD: round toward minus infinity (roundTowardNegative in IEEE 754-2008),
 */

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
	if(PN > 99) {
		//need to increase the size of char coefficientFormatCStr;
		throw std::runtime_error("output only supports precision <= 99");
	}
    sprintf(coefficientFormatCStr, "%%.%dg", PN);
	//cout << "'" << coefficientFormatCStr << "'" << endl;
}

namespace flowstar
{
inline void setMode(int mode) {
	if(lastUsed != mode) {
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

Real::Real(const Real & real)
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

void Real::abs(Real & real) const
{
	mpfr_abs(real.value, value, MPFR_RNDU);
}

void Real::abs_assign()
{
	mpfr_abs(value, value, MPFR_RNDU);
}

void Real::to_sym_int(Interval & I) const
{
	I.lo = getValue_RNDD();
	I.up = getValue_RNDU();
}

void Real::exp_RNDU(Real & result) const
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

void Real::rec(Real & result) const
{
	mpfr_ui_div(result.value, 1L, value, MPFR_RNDN);
}

void Real::add_RNDD(Real & result, const Real & real) const
{
	mpfr_add(result.value, value, real.value, MPFR_RNDD);
}

void Real::add_assign_RNDD(const Real & real)
{
	mpfr_add(value, value, real.value, MPFR_RNDD);
}

void Real::add_RNDU(Real & result, const Real & real) const
{
	mpfr_add(result.value, value, real.value, MPFR_RNDU);
}

void Real::add_assign_RNDU(const Real & real)
{
	mpfr_add(value, value, real.value, MPFR_RNDU);
}

void Real::add_RNDN(Real & result, const Real & real) const
{
	mpfr_add(result.value, value, real.value, MPFR_RNDN);
}

void Real::add_assign_RNDN(const Real & real)
{
	mpfr_add(value, value, real.value, MPFR_RNDN);
}

void Real::sub_RNDD(Real & result, const Real & real) const
{
	mpfr_sub(result.value, value, real.value, MPFR_RNDD);
}

void Real::sub_assign_RNDD(const Real & real)
{
	mpfr_sub(value, value, real.value, MPFR_RNDD);
}

void Real::sub_RNDU(Real & result, const Real & real) const
{
	mpfr_sub(result.value, value, real.value, MPFR_RNDU);
}

void Real::sub_assign_RNDU(const Real & real)
{
	mpfr_sub(value, value, real.value, MPFR_RNDU);
}

void Real::mul_RNDD(Real & result, const Real & real) const
{
	mpfr_mul(result.value, value, real.value, MPFR_RNDD);
}

void Real::mul_assign_RNDD(const Real & real)
{
	mpfr_mul(value, value, real.value, MPFR_RNDD);
}

void Real::mul_RNDU(Real & result, const Real & real) const
{
	mpfr_mul(result.value, value, real.value, MPFR_RNDU);
}

void Real::mul_assign_RNDU(const Real & real)
{
	mpfr_mul(value, value, real.value, MPFR_RNDU);
}

void Real::mul_RNDD(Real & result, const int n) const
{
	mpfr_mul_si(result.value, value, n, MPFR_RNDD);
}

void Real::mul_assign_RNDD(const int n)
{
	mpfr_mul_si(value, value, n, MPFR_RNDD);
}

void Real::mul_RNDU(Real & result, const int n) const
{
	mpfr_mul_si(result.value, value, n, MPFR_RNDU);
}

void Real::mul_assign_RNDU(const int n)
{
	mpfr_mul_si(value, value, n, MPFR_RNDU);
}

void Real::div_RNDD(Real & result, const Real & real) const
{
	mpfr_div(result.value, value, real.value, MPFR_RNDD);
}

void Real::div_assign_RNDD(const Real & real)
{
	mpfr_div(value, value, real.value, MPFR_RNDD);
}

void Real::div_RNDU(Real & result, const Real & real) const
{
	mpfr_div(result.value, value, real.value, MPFR_RNDU);
}

void Real::div_assign_RNDU(const Real & real)
{
	mpfr_div(value, value, real.value, MPFR_RNDU);
}

void Real::div_RNDD(Real & result, const int n) const
{
	mpfr_div_si(result.value, value, n, MPFR_RNDD);
}

void Real::div_assign_RNDD(const int n)
{
	mpfr_div_si(value, value, n, MPFR_RNDD);
}

void Real::div_RNDU(Real & result, const int n) const
{
	mpfr_div_si(result.value, value, n, MPFR_RNDU);
}

void Real::div_assign_RNDU(const int n)
{
	mpfr_div_si(value, value, n, MPFR_RNDU);
}

void Real::output(FILE *fp) const
{
	mpfr_out_str(fp, 10, PN, value, MPFR_RNDN);
}

Real & Real::operator += (const Real & r)
{
	mpfr_add(value, value, r.value, MPFR_RNDN);
	return *this;
}

Real & Real::operator -= (const Real & r)
{
	mpfr_sub(value, value, r.value, MPFR_RNDN);
	return *this;
}

Real & Real::operator *= (const Real & r)
{
	mpfr_mul(value, value, r.value, MPFR_RNDN);
	return *this;
}

Real & Real::operator /= (const Real & r)
{
	mpfr_div(value, value, r.value, MPFR_RNDN);
	return *this;
}

Real & Real::operator += (const double d)
{
	mpfr_add_d(value, value, d, MPFR_RNDN);
	return *this;
}

Real & Real::operator -= (const double d)
{
	mpfr_sub_d(value, value, d, MPFR_RNDN);
	return *this;
}

Real & Real::operator *= (const double d)
{
	mpfr_mul_d(value, value, d, MPFR_RNDN);
	return *this;
}

Real & Real::operator /= (const double d)
{
	mpfr_div_d(value, value, d, MPFR_RNDN);
	return *this;
}

Real Real::operator + (const Real & r) const
{
	Real result = *this;
	result += r;
	return result;
}

Real Real::operator - (const Real & r) const
{
	Real result = *this;
	result -= r;
	return result;
}

Real Real::operator * (const Real & r) const
{
	Real result = *this;
	result *= r;
	return result;
}

Real Real::operator / (const Real & r) const
{
	Real result = *this;
	result /= r;
	return result;
}

bool Real::operator == (const Real & r) const
{
	if(mpfr_cmp(value, r.value) == 0)
	{
		return true;
	}
	else
	{
		return false;
	}
}

bool Real::operator != (const Real & r) const
{
	if(mpfr_cmp(value, r.value) == 0)
	{
		return false;
	}
	else
	{
		return true;
	}
}

bool Real::operator >= (const Real & r) const
{
	if(mpfr_cmp(value, r.value) >= 0)
	{
		return true;
	}
	else
	{
		return false;
	}
}

bool Real::operator > (const Real & r) const
{
	if(mpfr_cmp(value, r.value) > 0)
	{
		return true;
	}
	else
	{
		return false;
	}
}

Real & Real::operator = (const Real & r)
{
	if(this == &r)
		return *this;

	mpfr_set(value, r.value, MPFR_RNDN);
	return *this;
}


Interval::Interval()
{
    lo = 0.0;
    up = 0.0;
}

Interval::Interval(const double c)
{
	//std::fesetround(FE_DOWNWARD);
    lo = c;
	//std::fesetround(FE_UPWARD);
    up = c;
}

Interval::Interval(const double l, const double u)
{
    lo = l;
    up = u;
}

Interval::Interval(const char *strLo, const char *strUp)
{
	saveMode();
	setMode(FE_DOWNWARD);
    lo = std::stod(strLo);
	setMode(FE_UPWARD);
	up = std::stod(strUp);
	restoreMode();
}

Interval::Interval(const Interval & I)
{
	lo = I.lo;
	up = I.up;
}

//TODO is this necessary?
Interval::~Interval() {

}

void Interval::set(const double l, const double u)
{
	lo = l;
    up = u;
}

void Interval::set(const double c)
{
	lo = c;
	up = c;
}

void Interval::setInf(const double l)
{
	lo = l;
}

void Interval::setInf(const Interval & I)
{
	lo = I.lo;
}

void Interval::setSup(const double u)
{
	up = u;
}

void Interval::setSup(const Interval & S)
{
	up = S.up;
}

void Interval::split(Interval & left, Interval & right) const
{
	saveMode();
	left.lo = lo;
	setMode(FE_UPWARD);
	left.up = (lo + up)/2.0;
	setMode(FE_DOWNWARD);
	right.lo = (lo + up)/2.0;
	right.up = up;
	restoreMode();
}

void Interval::split(std::list<Interval> & result, const int n) const
{
	throw std::runtime_error("'Interval::split(list<Interval> & result, const int n) const' not ported!");
}

void Interval::set_inf()
{
	lo = -1;
 	up = 1;
}

double Interval::sup() const
{
	return up;
}

double Interval::inf() const
{
	return lo;
}

void Interval::sup(Interval & S) const
{
	S.lo = up;
	S.up = up;
}

void Interval::inf(Interval & I) const
{
	I.lo = up;
	I.up = up;
}

double Interval::midpoint() const
{
	saveMode();
	setMode(FE_TONEAREST);
	return (lo + up) / 2.0;
	restoreMode();
}

void Interval::midpoint(Interval & M) const
{
	saveMode();
	setMode(FE_DOWNWARD);
	M.lo = (lo + up)/2.0;
	setMode(FE_UPWARD);
 	M.up = (lo + up)/2.0;
	restoreMode();
}

void Interval::remove_midpoint(Interval & M)
{
	saveMode();
	setMode(FE_DOWNWARD);
	M.lo = (lo + up)/2.0;
	setMode(FE_UPWARD);
	M.up = (lo + up)/2.0;
	//std::fesetround(FE_UPWARD);
	up -= M.lo;
	setMode(FE_DOWNWARD);
	lo -= M.up;
	restoreMode();
}

void Interval::remove_midpoint()
{
	double tmp1, tmp2;

	saveMode();
	setMode(FE_DOWNWARD);
	tmp1 = (lo + up)/2.0;
	setMode(FE_UPWARD);
	tmp2 = (lo + up)/2.0;
	//std::fesetround(FE_UPWARD);
	up -= tmp2;
	setMode(FE_DOWNWARD);
	lo -= tmp1;
	restoreMode();
}

Interval Interval::intersect(const Interval & I) const
{
	Interval result;

	if(lo > I.lo) {
	result.lo = lo;
	} else {
	result.lo = I.lo;
	}

	if(up > I.up) {
		result.up = I.up;
	} else {
		result.up = up;
	}

	return result;
}

void Interval::intersect_assign(const Interval & I)
{
	if(lo < I.lo) {
		lo = I.lo;
	}

	if(up > I.up) {
		up = I.up;
	}
}

void Interval::bloat(const double e)
{
	saveMode();
	setMode(FE_DOWNWARD);
	lo -= e;
	setMode(FE_UPWARD);
	up += e;
	restoreMode();
}

bool Interval::within(const Interval & I, const double e) const
{
	double d;

	//TODO don't this is necessary, but leaving it here now

	saveMode();
	setMode(FE_UPWARD);
	if(up >= I.up) {
		//std::fesetround(FE_UPWARD);
    	d = up - I.up;
	} else {
		//std::fesetround(FE_DOWNWARD);
    	//d = up - I.up;
    	d = I.up - up;
	}

	//not needed now
	//std::fesetround(FE_UPWARD);
	//d = fabs(d);

	if(d > e) {
		return false;
	}

	if(lo >= I.lo) {
		//std::fesetround(FE_UPWARD);
		d = lo - I.lo;
	} else {
		//std::fesetround(FE_DOWNWARD);
		d = I.lo - lo;
	}

	//not needed now
	setMode(FE_DOWNWARD);
	d = fabs(d);

	if(d > e) {
		return false;
	}
	restoreMode();

	return true;
}

double Interval::width() const
{
	saveMode();
	setMode(FE_UPWARD);
	return up - lo;
	restoreMode();
}

void Interval::width(Interval & W) const
{
	saveMode();
	setMode(FE_UPWARD);
	W.lo = up - lo;
	W.up = W.up;
	restoreMode();
}

double Interval::mag() const
{
	//I assume that fabs will only change sign bit (no rounding needed)
	double inf = fabs(lo);
	double sup = fabs(up);
	return inf < sup ? sup : inf;
}

void Interval::mag(Interval & M) const
{
	//I assume that fabs will only change sign bit (no rounding needed)
	double tmp1 = fabs(lo);
    double tmp2 = fabs(up);;

	if(tmp1 > tmp2) {
		M.lo = tmp1;
    	M.up = tmp1;
	} else {
		M.lo = tmp2;
    	M.up = tmp2;
	}
}

void Interval::abs(Interval & result) const
{
	//I assume that fabs will only change sign bit (no rounding needed)
	double tmp1 = fabs(lo);
	double tmp2 = fabs(up);

	if(tmp1 > tmp2) {
		result.lo = tmp2;
		result.up = tmp1;
	} else {
		result.lo = tmp1;
		result.up = tmp2;
	}
}

void Interval::abs_assign()
{
	double tmp1 = fabs(lo);
	double tmp2 = fabs(up);

	if(tmp1 > tmp2) {
		lo = tmp2;
		up = tmp1;
	} else {
		lo = tmp1;
		up = tmp2;
	}
}

bool Interval::subseteq(const Interval & I) const
{
	return (I.lo <= lo) && (I.up >= up);
}

bool Interval::supseteq(const Interval & I) const
{
	return (lo <= I.lo) && (up >= I.up);
}

bool Interval::valid() const
{
	return up >= lo;
}

bool Interval::operator == (const Interval & I) const
{
	return (lo == I.lo) && (up == I.up);
}

bool Interval::operator != (const Interval & I) const
{
	return (lo != I.lo) || (up != I.up);
}

bool Interval::operator > (const Interval & I) const
{
	return lo > I.up;
}

bool Interval::operator < (const Interval & I) const
{
	return up < I.lo;
}

bool Interval::operator <= (const Interval & I) const
{
	//why not <=?
	//return ( (mpfr_cmp(lo, I.lo) < 0) );
	return lo < I.lo;
}

bool Interval::operator >= (const Interval & I) const
{
	return up > I.up;
}

bool Interval::smallereq(const Interval & I) const
{
	return up <= I.lo;
}

Interval & Interval::operator = (const Interval & I)
{
	if(this == &I)
		return *this;	// check for self assignment

    lo = I.lo;
	up = I.up;

	return *this;
}

Interval & Interval::operator += (const Interval & I)
{
	saveMode();
    if(lastUsed == FE_DOWNWARD) {
    	lo += I.lo;
    	std::fesetround(FE_UPWARD);
    	up += I.up;
    	lastUsed = FE_UPWARD;
  	} else {
    	if (lastUsed != FE_UPWARD) {
      		std::fesetround(FE_UPWARD);
    	}
    	up += I.up;
	  	std::fesetround(FE_DOWNWARD);
    	lo += I.lo;
    	lastUsed = FE_DOWNWARD;
  	}
  	restoreMode();

	return *this;
}

Interval & Interval::operator -= (const Interval & I)
{
	saveMode();
	setMode(FE_DOWNWARD);
	lo -= I.up;
	setMode(FE_UPWARD);
	up -= I.lo;
	restoreMode();
	return *this;
}

inline double Interval::mulMin(const Interval & I) const {
	double lolo, loup, uplo, upup, min;
	// compute the lower bound
	lolo = lo * I.lo;
	loup = lo * I.up;
	uplo = up * I.lo;
	upup = up * I.up;

	min = lolo;
	if (min > loup) {
		min = loup;
	}
	if (min > uplo) {
		min = uplo;
	}
	if (min > upup) {
		min = upup;
	}
	return min;
}


inline double Interval::mulMax(const Interval & I) const {
	double lolo, loup, uplo, upup, max;
	lolo = lo * I.lo;
	loup = lo * I.up;
	uplo = up * I.lo;
	upup = up * I.up;

	max = lolo;
	if (max < loup) {
		max = loup;
	}
	if (max < uplo) {
		max = uplo;
	}
	if (max < upup) {
		max = upup;
	}
	return max;
}

//*
Interval & Interval::operator *= (const Interval & I)
{
	double min, max;
	saveMode();
    if(lastUsed == FE_DOWNWARD) {
		//std::fesetround(FE_DOWNWARD);// can skip this one
		min = mulMin(I);
    	setMode(FE_UPWARD);
		max = mulMax(I);
    	lastUsed = FE_UPWARD;
	} else {
		if (lastUsed != FE_UPWARD) { //can possibly skip this one
      		setMode(FE_UPWARD);
    	}
	  	max = mulMax(I);
    	setMode(FE_DOWNWARD);
	  	min = mulMin(I);
		lastUsed = FE_DOWNWARD;
  	}

	lo = min;
	up = max;
	restoreMode();

	return *this;
}//*/

/*
Interval & Interval::operator *= (const Interval & I)
{
  double lolo, loup, uplo, upup, min, max;

	// compute the lower bound
	std::fesetround(FE_DOWNWARD);
	lolo = lo * I.lo;
	loup = lo * I.up;
	uplo = up * I.lo;
	upup = up * I.up;

	min = lolo;
	if(min > loup) {
		min = loup;
	}
	if(min > uplo) {
		min = uplo;
	}
	if(min > upup) {
		min = upup;
	}

	std::fesetround(FE_UPWARD);
	lolo = lo * I.lo;
	loup = lo * I.up;
	uplo = up * I.lo;
	upup = up * I.up;

	max = lolo;
	if(max < loup) {
		max = loup;
	}
	if(max < uplo) {
		max = uplo;
	}
	if(max < upup) {
		max = upup;
	}

	lo = min;
	up = max;

	return *this;
}
//*/

Interval & Interval::operator /= (const Interval & I)
{
	Interval tmp;

	I.rec(tmp);
	*this *= tmp;

	return *this;
}

Interval & Interval::operator ++ ()
{
	saveMode();
	setMode(FE_DOWNWARD);
	lo++;
	setMode(FE_UPWARD);
	up++;
	restoreMode();

	return *this;
}

Interval & Interval::operator -- ()
{
	saveMode();
	setMode(FE_DOWNWARD);
	lo--;
	setMode(FE_UPWARD);
	up--;
	restoreMode();

	return *this;
}

const Interval Interval::operator + (const Interval & I) const
{
	Interval result = *this;
	result += I;
	return result;
}

const Interval Interval::operator - (const Interval & I) const
{
	Interval result = *this;
	result -= I;
	return result;
}

const Interval Interval::operator * (const Interval & I) const
{
	Interval result = *this;
	result *= I;
	return result;
}

const Interval Interval::operator / (const Interval & I) const
{
	Interval result = *this;
	result /= I;
	return result;
}

void Interval::sqrt(Interval & result) const
{
	if(lo < 0) {
		printf("Exception: Square root of a negative number.\n");
		exit(1);
	}
	saveMode();
	setMode(FE_DOWNWARD);
	result.lo = std::sqrt(lo);
	setMode(FE_UPWARD);
	result.up = std::sqrt(up);
	restoreMode();
}

void Interval::inv(Interval & result) const
{
  //I assume that '-' will only change sign bit (no rounding needed)
	//std::fesetround(FE_DOWNWARD);
	result.lo = -up;
	//std::fesetround(FE_UPWARD);
	result.up = -lo;
}

void Interval::rec(Interval & result) const
{
	saveMode();
	if (lo <= 0 && up >= 0) {
		printf("Exception: Divided by 0.\n");
		exit(1);
	} else {
		setMode(FE_DOWNWARD);
    	result.lo = 1.0/up;
		setMode(FE_UPWARD);
    	result.up = 1.0/lo;
	}
	restoreMode();
}

void Interval::sqrt_assign()
{
	saveMode();
	if(lo < 0) {
		printf("Exception: Square root of a negative number.\n");
		exit(1);
	}
	setMode(FE_DOWNWARD);
	lo = std::sqrt(lo);
	setMode(FE_UPWARD);
	up = std::sqrt(up);
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
	setMode(FE_DOWNWARD);
	lo += c;
	setMode(FE_UPWARD);
	up += c;
	restoreMode();
}

void Interval::sub_assign(const double c)
{
	saveMode();
	setMode(FE_DOWNWARD);
	lo -= c;
	setMode(FE_UPWARD);
	up -= c;
	restoreMode();
}

void Interval::mul_assign(const double c)
{
	Interval result;

	saveMode();
	if(c > 0) {
    	setMode(FE_DOWNWARD);
    	result.lo = lo * c;
    	setMode(FE_UPWARD);
    	result.up = up * c;
	} else {
    	setMode(FE_DOWNWARD);
    	result.lo = up * c;
    	setMode(FE_UPWARD);
    	result.up = lo * c;
	}
	restoreMode();

	*this = result;
}

void Interval::div_assign(const double c)
{
	Interval result;

	saveMode();
	if (c > 0) {
    	setMode(FE_DOWNWARD);
    	result.lo = lo / c;
    	setMode(FE_UPWARD);
    result.up = up / c;
	} else {
    	setMode(FE_DOWNWARD);
    result.lo = up / c;
    	setMode(FE_UPWARD);
    	result.up = lo / c;
	}
	restoreMode();

	*this = result;
}

Interval Interval::pow(const int n) const
{
	Interval result;

	saveMode();
	if (n % 2 == 1) {	// n is odd
    	setMode(FE_DOWNWARD);
    	result.lo = std::pow(lo, n);
    	setMode(FE_UPWARD);
    	result.up = std::pow(up, n);
		restoreMode();
		return result;
	}
	// n is even
	if(lo >= 0) {			// 0 <= lo <= up
		setMode(FE_DOWNWARD);
		result.lo = std::pow(lo, n);
		setMode(FE_UPWARD);
		result.up = std::pow(up, n);
	} else if(up <= 0)	{	// lo <= up <= 0
		setMode(FE_DOWNWARD);
		result.lo = std::pow(up, n);
		setMode(FE_UPWARD);
		result.up = std::pow(lo, n);
	} else {									// lo < 0 < up
		double tmp1, tmp2;
		setMode(FE_UPWARD);
		tmp1 = std::pow(lo, n);
		tmp2 = std::pow(up, n);
		if(tmp1 >= tmp2) {
			result.up = tmp1;
		} else {
			result.up = tmp2;
		}
		//wasn't present in Flow* (but putting it here for being explicit)
		result.lo = 0;
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
	setMode(FE_DOWNWARD);
	result.lo = std::exp(lo);
	setMode(FE_UPWARD);
	result.up = std::exp(up);
	restoreMode();

	return result;
}

Interval Interval::sin() const
{
  throw std::runtime_error("'Interval::sin() not ported!");
}

Interval Interval::cos() const
{
  throw std::runtime_error("'Interval::cos() not ported!");
}

Interval Interval::log() const
{
	if(lo <= 0) {
		printf("Exception: Logarithm of a non-positive number.\n");
		exit(1);
	} else {
		Interval result;

		saveMode();
	  	throw std::runtime_error("std::exp function is not precise (after 17 digits");
	  	setMode(FE_DOWNWARD);
	  	result.lo = std::log(lo);
	  	setMode(FE_UPWARD);
	  	result.up = std::log(up);
		restoreMode();

		return result;
	}
}

void Interval::pow_assign(const int n)
{
	saveMode();
	if(n % 2 == 1)		// n is odd
	{
		setMode(FE_DOWNWARD);
		lo = std::pow(lo, n);
		setMode(FE_UPWARD);
		up = std::pow(up, n);
		restoreMode();
		return;
	}
	// n is even
	if(lo >= 0) {		// 0 <= lo <= up
		setMode(FE_DOWNWARD);
		lo = std::pow(lo, n);
		setMode(FE_UPWARD);
		up = std::pow(up, n);
	} else if(up <= 0) {		// lo <= up <= 0
		setMode(FE_DOWNWARD);
		double tmp = std::pow(up, n);
		setMode(FE_UPWARD);
		up = std::pow(lo, n);
		lo = tmp;
	} else {							// lo < 0 < up
		double tmp1, tmp2;
		setMode(FE_UPWARD);
		tmp1 = std::pow(lo, n);
		tmp2 = std::pow(up, n);
		if(tmp1 >= tmp2) {
			up = tmp1;
		} else {
			up = tmp2;
		}
		lo = 0;
	}
	restoreMode();
}

void Interval::exp_assign()
{
	saveMode();
	throw std::runtime_error("std::exp function is not precise");
	setMode(FE_DOWNWARD);
	lo = std::exp(lo);
	setMode(FE_UPWARD);
	up = std::exp(up);
	restoreMode();
}

void Interval::sin_assign()
{
	throw std::runtime_error("'Interval::sin_assign() not ported!");
}

void Interval::cos_assign()
{
	throw std::runtime_error("'Interval::cos_assign() not ported!");
}

void Interval::log_assign()
{
	if (lo <= 0) {
		printf("Exception: Logarithm of a non-positive number.\n");
		exit(1);
	} else {
		throw std::runtime_error("std::exp function is not precise (after 17 digits");
		saveMode();
		setMode(FE_DOWNWARD);
		lo = std::log(lo);
		setMode(FE_UPWARD);
		up = std::log(up);
		restoreMode();
	}
}

double Interval::widthRatio(const Interval & I) const
{
	double width1, width2, ratio;

	saveMode();
	setMode(FE_UPWARD);
	width1 = up - lo;
	width2 = I.up - I.lo;

	ratio = width2 / width1;		// we assume that width1 >= width2
	restoreMode();

	return ratio;
}

void Interval::toString(std::string & result) const
{
  //mlog1("(string) version");
	char strTemp[30];
	saveMode();

	std::string strInt;
	strInt += '[';

  //std::fesetround(FE_DOWNWARD);
	setMode(FE_DOWNWARD);
	sprintf(strTemp, "%.10f", lo);
	std::string strLo(strTemp);

	strInt += strLo;
	strInt += ' ';
	strInt += ',';
	strInt += ' ';

    //std::fesetround(FE_UPWARD);
	setMode(FE_UPWARD);
	sprintf(strTemp, "%.10f", up);
	std::string strUp(strTemp);
	strInt += strUp;
	strInt += ']';
	restoreMode();

	result = strInt;
}

void Interval::dump(FILE *fp) const
{
	saveMode();
	if(coefficientOutputFormatSet == false) {
		setCoefficientFormatCStr();
	}
	fprintf (fp, "[");

	//15 is PN in Flow* (but it's arbitrary anyway)
  //std::fesetround(FE_DOWNWARD);
	setMode(FE_TONEAREST);
	fprintf (fp, coefficientFormatCStr, lo);
	fprintf(fp, " , ");
	//std::fesetround(FE_UPWARD);
	//setMode(FE_TONEAREST);
	fprintf (fp, coefficientFormatCStr, up);

	fprintf(fp, "]");
	restoreMode();
}

void Interval::output(FILE * fp, const char * msg, const char * msg2) const
{
	if(coefficientOutputFormatSet == false) {
		setCoefficientFormatCStr();
	}
	fprintf (fp, "%s [ ", msg);

	//15 is PN in Flow* (but it's arbitrary anyway)
  //std::fesetround(FE_DOWNWARD);
	setMode(FE_TONEAREST);
	fprintf (fp, coefficientFormatCStr, lo);
	fprintf(fp, " , ");
  //std::fesetround(FE_UPWARD);
	//setMode(FE_TONEAREST);
	fprintf (fp, coefficientFormatCStr, up);

	fprintf(fp, " ] %s", msg2);
	saveMode();
}

bool subseteq(const std::vector<Interval> & v1, const std::vector<Interval> & v2) {
	if (v1.size() != v2.size())
    	throw std::invalid_argument("Different domains of vectors");
  	for (int i = 0; i < v1.size(); i++) {
    	if (v1[i].subseteq(v2[i]) == false) {
    		return false;
    	}
	}
  	return true;
}

//--new from 2.1
Interval::Interval(const Real & r)
{
	lo = r.getValue_RNDD();
	up = r.getValue_RNDU();
}

Interval::Interval(const Real & c, const Real & r)
{
	saveMode();
	setMode(FE_DOWNWARD);
	lo = c.getValue_RNDD() - r.getValue_RNDU();
	setMode(FE_UPWARD);
  up = c.getValue_RNDU() + r.getValue_RNDU();
	restoreMode();
}

Interval::Interval(const Real & l, const Real & u, const int n)
{
	lo = l.getValue_RNDD();
	up = u.getValue_RNDU();
}


bool Interval::isZero() const
{
	Interval intZero;

	if(this->subseteq(intZero))
	{
		return true;
	}
	else
	{
		return false;
	}
}

void Interval::set(const Real & r)
{
	lo = r.getValue_RNDD();
	up = r.getValue_RNDU();
}

void Interval::sup(Real & u) const
{
	mpfr_set_d(u.value, up, MPFR_RNDU);
}

void Interval::inf(Real & l) const
{
	mpfr_set_d(l.value, lo, MPFR_RNDD);
}


void Interval::midpoint(Real & mid) const
{
	saveMode();
	setMode(FE_TONEAREST);
	mpfr_set_d(mid.value, (lo + up) / 2.0, MPFR_RNDN);
	restoreMode();
}

void Interval::toCenterForm(Real & center, Real & radius) const
{
	saveMode();
	setMode(FE_TONEAREST);
	mpfr_set_d(center.value, (lo + up) / 2.0, MPFR_RNDN);

	setMode(FE_UPWARD);
	mpfr_set_d(radius.value, (up - lo) / 2.0, MPFR_RNDU);
	restoreMode();
}

void Interval::bloat(const Real & e)
{
	saveMode();
	setMode(FE_DOWNWARD);
	lo -= e.getValue_RNDU(); //NOT sure if U or D is correct
	setMode(FE_UPWARD);
	lo += e.getValue_RNDU(); //see above comment
	restoreMode();
}


void Interval::mag(Real & m) const
{
	double tmp1 = fabs(lo), tmp2 = fabs(up);

	if(tmp1 >= tmp2) {
		mpfr_set_d(m.value, tmp1, MPFR_RNDN);
		return;
	}
	mpfr_set_d(m.value, tmp2, MPFR_RNDN);
}


Interval & Interval::operator = (const Real & r)
{
	lo = r.getValue_RNDD();
	up = r.getValue_RNDU();

	return *this;
}

Interval & Interval::operator = (const double d)
{
	lo = d;
	up = d;

	return *this;
}

Interval & Interval::operator += (const double c)
{
	saveMode();
	setMode(FE_DOWNWARD);
	lo += c;
	setMode(FE_UPWARD);
	up += c;
	restoreMode();

	return *this;
}

Interval & Interval::operator -= (const double c)
{
	saveMode();
	setMode(FE_DOWNWARD);
	lo -= c;
	setMode(FE_UPWARD);
	up -= c;
	restoreMode();

	return *this;
}


Interval & Interval::operator *= (const double c)
{
	saveMode();
	if(c >= 0) {
		setMode(FE_DOWNWARD);
		lo *= c;
		setMode(FE_UPWARD);
		up *= c;
	} else {
		double temp = lo;
		setMode(FE_DOWNWARD);
		lo = up * c;
		setMode(FE_UPWARD);
		up = temp * c;
	}
	restoreMode();

	return *this;
}

Interval & Interval::operator /= (const double c)
{
	saveMode();
	if(c >= 0) {
		setMode(FE_DOWNWARD);
		lo /= c;
		setMode(FE_UPWARD);
		up /= c;
	} else {
		double temp = lo;
		setMode(FE_DOWNWARD);
		lo = up / c;
		setMode(FE_UPWARD);
		up = temp / c;
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
	if(c > 0) {
		setMode(FE_DOWNWARD);
		result.lo = lo * c;
		setMode(FE_UPWARD);
		result.up = up * c;
	} else {
		setMode(FE_DOWNWARD);
		result.lo = up * c;
		setMode(FE_UPWARD);
		result.up = lo * c;
	}
	restoreMode();

	return result;
}

const Interval Interval::operator / (const double c) const
{
	Interval result;

	saveMode();
	if(c > 0) {
		setMode(FE_DOWNWARD);
		result.lo = lo / c;
		setMode(FE_UPWARD);
		result.up = up / c;
	} else {
		setMode(FE_DOWNWARD);
		result.lo = up / c;
		setMode(FE_UPWARD);
		result.up = lo / c;
	}
	restoreMode();

	return result;
}

void Interval::mul_add(Interval *result, const Interval *intVec, const int size)
{
	double tmp1, tmp2, tmp_up, tmp_lo;

	saveMode();
	if (lo >= 0)
	{
		for (int i=0; i<size; ++i)
		{
			if (intVec[i].lo >= 0)
			{
				setMode(FE_DOWNWARD);
				tmp_lo = lo * intVec[i].lo;
				setMode(FE_UPWARD);
				tmp_up = up * intVec[i].up;
			}
			else if(intVec[i].up <= 0)
			{
				setMode(FE_DOWNWARD);
				tmp_lo = up * intVec[i].lo;
				setMode(FE_UPWARD);
				tmp_up = lo * intVec[i].up;
			}
			else
			{
				setMode(FE_DOWNWARD);
				tmp_lo = up * intVec[i].lo;
				setMode(FE_UPWARD);
				tmp_up = up * intVec[i].up;
			}

			setMode(FE_DOWNWARD);
			result[i].lo = result[i].lo + tmp_lo;
			setMode(FE_UPWARD);
			result[i].up = result[i].up + tmp_up;
		}
	}
	else if (up <= 0)
	{
		for (int i=0; i<size; ++i)
		{
			if (intVec[i].lo >= 0)
			{
				setMode(FE_DOWNWARD);
				tmp_lo = lo * intVec[i].up;
				setMode(FE_UPWARD);
				tmp_up = up * intVec[i].lo;
			}
			else if (intVec[i].up <= 0)
			{
				setMode(FE_DOWNWARD);
				tmp_lo = up * intVec[i].up;
				setMode(FE_UPWARD);
				tmp_up = lo * intVec[i].lo;
			}
			else
			{
				setMode(FE_DOWNWARD);
				tmp_lo = lo * intVec[i].up;
				setMode(FE_UPWARD);
				tmp_up = lo * intVec[i].lo;
			}
			setMode(FE_DOWNWARD);
			result[i].lo = result[i].lo + tmp_lo;
			setMode(FE_UPWARD);
			result[i].up = result[i].up + tmp_up;
		}
	}
	else
	{
		for(int i=0; i<size; ++i)
		{
			if(intVec[i].lo >= 0)
			{
				setMode(FE_DOWNWARD);
				tmp_lo = lo * intVec[i].up;
				setMode(FE_UPWARD);
				tmp_up = up * intVec[i].up;
			}
			else if(intVec[i].up <= 0)
			{
				setMode(FE_DOWNWARD);
				tmp_lo = up * intVec[i].lo;
				setMode(FE_UPWARD);
				tmp_up = lo * intVec[i].lo;
			}
			else
			{
				setMode(FE_DOWNWARD);
				tmp1 = lo * intVec[i].up;
				tmp2 = up * intVec[i].lo;

				if(tmp1 > tmp2)
				{
					tmp_lo = tmp2;
				}
				else
				{
					tmp_lo = tmp1;
				}

				setMode(FE_UPWARD);
				tmp1 = lo * intVec[i].lo;
				tmp2 = up * intVec[i].up;

				if(tmp1 > tmp2)
				{
					tmp_up = tmp1;
				}
				else
				{
					tmp_up = tmp2;
				}
			}

			setMode(FE_DOWNWARD);
			result[i].lo = result[i].lo + tmp_lo;
			setMode(FE_UPWARD);
			result[i].up = result[i].up + tmp_up;
		}
	}
	restoreMode();
}
