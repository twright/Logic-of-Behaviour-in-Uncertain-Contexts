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
	I.lo = -getValue_RNDD();
	I.up = getValue_RNDU();
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
		lo = -0.0;
		up = 0.0;
		
	}

	Interval::Interval(const double c)
	{
		lo = -c;
		up = c;
	}

	Interval::Interval(const double l, const double u)
	{
		lo = -l;
		up = u;
	}

	Interval::Interval(const char* strLo, const char* strUp)
	{
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		lo = std::stod("-"+std::string(strLo));
		//setMode(FE_UPWARD);
		up = std::stod(strUp);
		restoreMode();
	}

	Interval::Interval(const Interval& I)
	{
		lo = I.lo;
		up = I.up;
	}

    Interval::~Interval()
	{
	}

	void Interval::set (const double l, const double u)
	{
		lo = -l;
		up = u;
	}

	void Interval::set(const double c)
	{
		lo = -c;
		up = c;
	}

	void Interval::setInf(const double l)
	{
		lo = -l;
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

	void Interval::split(Interval& left, Interval & right) const
	{
		saveMode();
		left.lo = lo;
		setMode(FE_UPWARD);
		left.up = (-lo + up) / 2.0;
		right.lo = (lo + -up) / 2.0;
		right.up = up;
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
		lo=1;
		up=1;
	}

	double Interval::sup() const
	{
		return up;
	}

	double Interval::inf() const
	{
		return -lo;
	}

	void Interval::sup(Interval & S) const
	{
		S.lo = -up;
		S.up = up;
	}

	void Interval::inf(Interval& I) const
	{
		I.lo = lo;
		I.up = -lo;
	} // two functions with different names do the same thing...

	double Interval::midpoint() const
	{
		saveMode();
		setMode(FE_TONEAREST);
		return (-lo + up) / 2.0;
		restoreMode();
		//unsure
	}

	void Interval::midpoint(Interval & M)const
	{
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		M.lo = (lo + -up) / 2.0;
		//setMode(FE_UPWARD);
		M.up = (-lo + up) / 2.0;
		restoreMode();
		
	}

	void Interval::remove_midpoint(Interval & M)
	{
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		M.lo = (lo + -up) / 2.0;
		//setMode(FE_UPWARD);
		M.up = (-lo + up) / 2.0;
		//std::fesetround(FE_UPWARD);
		up += M.lo; //signchange
		//setMode(FE_DOWNWARD);
		lo += M.up;
		restoreMode();
	}

	void Interval::remove_midpoint()
	{
		double tmp1, tmp2;
		//same as before but saving temporary values into temp doubles instead of interval

		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		tmp1 = (-lo + up) / 2.0;
		//setMode(FE_UPWARD);
		tmp2 = (lo - up) / 2.0;
		//std::fesetround(FE_UPWARD);
		up += tmp2;
		//setMode(FE_DOWNWARD);
		lo += tmp1;
		restoreMode();
	}

	Interval Interval::intersect(const Interval & I) const //returning intersection of two intervals
	{
		Interval result;
		//flipping signs because of minus storing
		if(lo<I.lo)
		{
			result.lo = lo;
		}
		else
		{
			result.lo = I.lo;
		}
		if (up > I.up) {
			result.up = I.up;
		}
		else {
			result.up = up;
		}

		return result;
	}

	void Interval::intersect_assign(const Interval & I) //assigning the intersection to left side interval
	{
		if(lo>I.lo)
		{
			lo = I.lo;
		}
		if(up>I.up)
		{
			up = I.up;
		}
	}

	void Interval::bloat (const double e)
	{
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		lo += e;
		//setMode(FE_UPWARD);
		up += e;
		restoreMode();
	}

	bool Interval::within(const Interval& I, const double e) const
	{
		double d;

		//TODO don't this is necessary, but leaving it here now

		saveMode();
		setMode(FE_UPWARD);
		if (up >= I.up) {
			//std::fesetround(FE_UPWARD);
			d = up - I.up;
		}
		else {
			//std::fesetround(FE_DOWNWARD);
			//d = up - I.up;
			d = I.up - up;
		}

		//not needed now
		//std::fesetround(FE_UPWARD);
		//d = fabs(d);

		if (d > e) {
			return false;
		}

		if (lo <= I.lo) {
			//std::fesetround(FE_UPWARD);
			d =  lo-I.lo;
		}
		else {
			//std::fesetround(FE_DOWNWARD);
			d = I.lo - lo;
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
		return up + lo;
	}

	void Interval::width(Interval& W) const
	{
		setMode(FE_UPWARD);
		W.lo = -lo-up;
		W.up = -W.lo; // is this necessary or a mistake?
		restoreMode();
	}

	double Interval::mag() const
	{
		//I assume that fabs will only change sign bit (no rounding needed)
		double inf = fabs(lo);
		double sup = fabs(up);
		return inf < sup ? sup : inf;
		// no change needed here
	}

	void Interval::mag(Interval& M) const
	{
		//I assume that fabs will only change sign bit (no rounding needed)
		double tmp1 = fabs(lo);
		double tmp2 = fabs(up);;

		if (tmp1 > tmp2) {
			M.lo = -tmp1;
			M.up = tmp1;
		}
		else {
			M.lo = -tmp2;
			M.up = tmp2;
		}
		//minuses added to lo limit saved into M
	}

	void Interval::abs(Interval& result) const
	{
		//I assume that fabs will only change sign bit (no rounding needed)
		double tmp1 = fabs(lo);
		double tmp2 = fabs(up);

		if (tmp1 > tmp2) {
			result.lo = -tmp2;
			result.up = tmp1;
		}
		else {
			result.lo = -tmp1;
			result.up = tmp2;
		}
		//minuses added to lo limit saved into result
	}

	void Interval::abs_assign()
	{
		double tmp1 = fabs(lo);
		double tmp2 = fabs(up);

		if (tmp1 > tmp2) {
			lo = -tmp2;
			up = tmp1;
		}
		else {
			lo = -tmp1;
			up = tmp2;
		}
		//minuses added to lo limit assignments
	}

	bool Interval::subseteq(const Interval& I) const
	{
		//flipped signs because -lo-s are compared
		if ((I.lo >= lo) && (I.up >= up))
			return true;
		return false;
	}

	bool Interval::supseteq(const Interval& I) const
	{
		//flipped signs because -lo-s are compared
		if ((lo >= I.lo) && (up >= I.up))
			return true;
		return false;
	}

	bool Interval::valid() const
	{
		if (up >= -lo) {
			return true;
		}
		return false;
	}

	bool Interval::operator == (const Interval& I) const
	{
		return (lo == I.lo) && (up == I.up);
	}

	bool Interval::operator != (const Interval& I) const
	{
		return (lo != I.lo) || (up != I.up);
	}

	bool Interval::operator > (const Interval& I) const
	{
		return -lo > I.up;
	}

	bool Interval::operator < (const Interval& I) const
	{
		return up < -I.lo;
	}

	bool Interval::operator <= (const Interval& I) const
	{
		//why not <=?
		//return ( (mpfr_cmp(lo, I.lo) < 0) );
		//flipped signs
		return lo > I.lo;
	}

	bool Interval::operator >= (const Interval& I) const
	{
		return up > I.up;
	}

	bool Interval::smallereq(const Interval& I) const
	{
		return up <= -I.lo;
	}

	Interval& Interval::operator = (const Interval& I)
	{
		if (this == &I)
			return *this;	// check for self assignment

		lo = I.lo;
		up = I.up;

		return *this;
	}

	Interval& Interval::operator += (const Interval& I)
	{
		saveMode();
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
		}
		restoreMode();

		return *this;
	}

	Interval& Interval::operator -= (const Interval& I)
	{
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		//switched signs
		lo += I.up;
		//setMode(FE_UPWARD);
		//switched signs
		up += I.lo;
		restoreMode();
		return *this;
	}

	inline double Interval::mulMin(const Interval& I) const {
		//modified to return -min to be saved immediately to lo
		double lolo, loup, uplo, upup, min;
		// compute the lower bound
		lolo = -lo * I.lo;
		loup = lo * I.up;
		uplo = up * I.lo;
		upup = -up * I.up;

		min = lolo;
		if (min < loup) {
			min = loup;
		}
		if (min < uplo) {
			min = uplo;
		}
		if (min < upup) {
			min = upup;
		}
		return min;
	}

	inline double Interval::mulMax(const Interval& I) const {
		double lolo, loup, uplo, upup, max;
		lolo = lo * I.lo;
		loup = -lo * I.up;
		uplo = up * -I.lo;
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

		lo = min;
		up = max;
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
		lo--; //sign switch here
		//setMode(FE_UPWARD);
		up++;
		restoreMode();

		return *this;
	}

	Interval& Interval::operator -- ()
	{
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		lo++;
		//setMode(FE_UPWARD);
		up--;
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
		if (lo > 0) { //flipping sign
			printf("Exception: Square root of a negative number.\n");
			exit(1);
		}
		saveMode();
		setMode(FE_DOWNWARD);
		result.lo = -std::sqrt(-lo);
		//setMode(FE_UPWARD);
		setMode(FE_UPWARD);
		result.up = std::sqrt(up);
		restoreMode();
	}

	void Interval::inv(Interval& result) const
	{
		//I assume that '-' will only change sign bit (no rounding needed)
		  //std::fesetround(FE_DOWNWARD);
		result.lo =up;
		//std::fesetround(FE_UPWARD);
		result.up = lo;
	}

	void Interval::rec(Interval& result) const
	{
		saveMode();
		if (lo >= 0 && up >= 0) {
			printf("Exception: Divided by 0.\n");
			exit(1);
		}
		else {
			//setMode(FE_DOWNWARD);
			setMode(FE_UPWARD);
			result.lo = -1.0 / up;
			result.up = -1.0 / lo;
		}
		restoreMode();
	}

	void Interval::sqrt_assign()
	{
		saveMode();
		if (lo > 0) {
			printf("Exception: Square root of a negative number.\n");
			exit(1);
		}
		
		setMode(FE_DOWNWARD);
		lo = -std::sqrt(-lo);
		//setMode(FE_UPWARD);
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
		setMode(FE_UPWARD);
		//setMode(FE_DOWNWARD);
		lo -= c;
		//setMode(FE_UPWARD);
		up += c;
		restoreMode();
	}

	void Interval::sub_assign(const double c)
	{
		saveMode();
		setMode(FE_UPWARD);
		//setMode(FE_DOWNWARD);
		lo += c;
		//setMode(FE_UPWARD);
		up -= c;
		restoreMode();
	}

	void Interval::mul_assign(const double c)
	{
		Interval result;

		saveMode();
		if (c > 0) {
			setMode(FE_UPWARD);
			//setMode(FE_DOWNWARD);
			result.lo = lo * c;
			//setMode(FE_UPWARD);
			result.up = up * c;
		}
		else {
			setMode(FE_UPWARD);
			//setMode(FE_DOWNWARD);
			result.lo = -up * c;
			//setMode(FE_UPWARD);
			result.up = -lo * c;
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
			result.lo = lo / c;
			//setMode(FE_UPWARD);
			result.up = up / c;
		}
		else {
			setMode(FE_UPWARD);
			//setMode(FE_DOWNWARD);
			result.lo = -up / c;
			//setMode(FE_UPWARD);
			result.up = -lo / c;
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
			result.lo = std::pow(lo, n); //low retains sign
			//setMode(FE_UPWARD);
			result.up = std::pow(up, n);
			restoreMode();
			return result;
		} 
		// n is even
		if (lo <= 0) {			// 0 <= lo <= up signs flipped
			//setMode(FE_DOWNWARD);
			result.lo = -std::pow(lo, n-1)*lo; //number def positive which means stores as def negative or 0
			//setMode(FE_UPWARD);
			result.up = std::pow(up, n);
		}
		else if (up <= 0) {	// lo <= up <= 0
			//setMode(FE_DOWNWARD);
			result.lo = std::pow(-up, n-1)*up; //number def positive which means stores as def negative or 0
			//setMode(FE_UPWARD);
			result.up = std::pow(lo, n);
		}
		else {									// lo < 0 < up
			double tmp1, tmp2;
			//setMode(FE_UPWARD);
			tmp1 = std::pow(lo, n);
			tmp2 = std::pow(up, n);
			if (tmp1 >= tmp2) {
				result.up = tmp1;
			}
			else {
				result.up = tmp2;
			}
			//wasn't present in Flow* (but putting it here for being explicit)
			result.lo = -0.0;
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
		result.lo = -std::exp(-lo);
		//setMode(FE_UPWARD);
		result.up = std::exp(up);
		restoreMode();

		return result;
	}

	Interval Interval::sin() const
	{
    double pi_up=0;
	double pi_lo=0;
	double tmp_up=0;
	double tmp_lo=0;
	saveMode();
	//setMode(FE_DOWNWARD);
	setMode(FE_UPWARD);
	pi_up=std::stod(str_pi_up);
	pi_lo=std::stod("-"+std::string(str_pi_lo)); //pi_lo is flipped because of rounding
	tmp_up=up/-pi_lo;
	tmp_up*=2;
	tmp_up=floor(tmp_up);
	//setMode(FE_DOWNWARD);
	tmp_lo=lo/pi_up;
	tmp_lo*=2;
	
	tmp_lo=ceil(tmp_lo);
	
	//setMode(FE_TONEAREST); //is that necessary

	int iUp= (int) tmp_up;
	int iLo= (int) tmp_lo; //flipped because lo is used to created

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
					result.lo=::sin(lo); //note that sin(x)=-sin(-x), since lo=-lo and we want to save -sin(x) there is no need to switch signs
					//setMode(FE_UPWARD); // upward rounding is still set
					result.up=::sin(up);
				}
				else
				{
					result.lo=1; //changed -1 to 1
					result.up=1;
					//don't think rounding modes are necessary here;
				}
				break;
			case 1:
			    result.up=1;
                //setMode(FE_DOWNWARD);
				tmp1=::sin(lo);
				tmp2=-::sin(up); //sign flipped using -tmp1 and -tmp2

				if(tmp1<tmp2) //sign flip
				{
					result.lo=tmp2;
				}
				else
				{
					result.lo=tmp1;
				}
				break;
			case 2:
			    result.up=1;
				//setMode(FE_DOWNWARD);
				result.lo=::sin(-up); //minus added to up
				break;
			case 3:
			    result.lo=1; //changed -1 to 1
				result.up=1;
				break;
			}
			break;
		case 1:
			switch(modUp)
			{
			case 0:
			    result.lo=1; //changed -1 to 1
				//setMode(FE_UPWARD);
				tmp1=::sin(-lo); //needs to negate lo
				tmp2=::sin(up);

				if(tmp1 > tmp2)
				{
					result.up=tmp1;
				}
				else
				{
					result.up=tmp2;
				}
				break;
			case 1:
				if(iPeriod == 0)
				{
					//setMode(FE_DOWNWARD);
					result.lo=::sin(-up);
					//setMode(FE_UPWARD);
					result.up=::sin(-lo);
				}
				else
				{
					result.lo=1; //changed -1 to 1
					result.up=1;
				}
				break;
			case 2:
			    //setMode(FE_DOWNWARD);
				result.lo=::sin(-up);
				//setMode(FE_UPWARD);
				result.up=::sin(-lo);
				break;
			case 3:
				result.lo=1;
				//setMode(FE_UPWARD);
				result.up=::sin(-lo);
				break;
			}
			break;
		case 2:
			switch(modUp)
			{
			case 0:
				result.lo=1;
				//setMode(FE_UPWARD);
				result.up=::sin(up);
				break;
			case 1:
			    result.lo=1;
				result.up=1;
				break;
			case 2:
				if(iPeriod == 0)
				{
					//setMode(FE_DOWNWARD);
					result.lo=::sin(-up);
					//setMode(FE_UPWARD);
					result.up=::sin(-lo);
				}
				else
				{
					result.lo=1;
					result.up=1;
				}
				break;
			case 3:
				result.lo=1;
				//setMode(FE_UPWARD);
				tmp1=::sin(-lo);
				tmp2=::sin(up);
				if(tmp1 > tmp2)
				{
					result.up=tmp1;
				}
				else
				{
					result.up=tmp2;
				}
				break;
			}
			break;
		case 3:
			switch(modUp)
			{
			case 0:
			    //setMode(FE_DOWNWARD);
				result.lo=::sin(lo);
				//setMode(FE_UPWARD);
				result.up=::sin(up);
				break;
			case 1:
			    //setMode(FE_DOWNWARD);
				result.lo=::sin(lo);
				result.up=1;
				break;
			case 2:
			    result.up=1;
				//setMode(FE_DOWNWARD);
				tmp1=::sin(lo);
				tmp2=::sin(-up);

				if(tmp1 < tmp2) //flipped sign
				{
					result.lo=tmp2;
				}
				else
				{
					result.lo=tmp1;
				}
				break;
			case 3:
				if(iPeriod == 0)
				{
					//setMode(FE_DOWNWARD);
					result.lo=::sin(lo);
					//setMode(FE_UPWARD);
					result.up=::sin(up);
				}
				else
				{
					result.lo=1;
					result.up=1;
				}
				break;
			}
			break;
		}
		restoreMode();

		return result;
	}
		throw std::runtime_error("'Interval::sin() not ported!");
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
	pi_up+=lo;
	//setMode(FE_DOWNWARD);
	pi_down+=up;
	Interval shift=Interval(-pi_up,pi_down);
	return shift.sin();
		//throw std::runtime_error("'Interval::cos() not ported!");
	}

	Interval Interval::log() const
	{
		if (lo >= 0) { //flipped sign
			printf("Exception: Logarithm of a non-positive number.\n");
			exit(1);
		}
		else {
			Interval result;

			saveMode();
			throw std::runtime_error("std::exp function is not precise (after 17 digits");
			//setMode(FE_DOWNWARD);
			setMode(FE_UPWARD);
			result.lo = -std::log(-lo);
			//setMode(FE_UPWARD);
			result.up = std::log(up);
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
			lo = std::pow(lo, n);
			//setMode(FE_UPWARD);
			up = std::pow(up, n);
			restoreMode();
			return;
		}
		// n is even
		if (lo <= 0) {		// 0 <= lo <= up flipped sign
			//setMode(FE_DOWNWARD);
			lo = -std::pow(lo, n-1)*lo;
			//setMode(FE_UPWARD);
			up = std::pow(up, n);
		}
		else if (up <= 0) {		// lo <= up <= 0
			//setMode(FE_DOWNWARD);
			double tmp = -std::pow(up, n-1)*up;
			//setMode(FE_UPWARD);
			up = std::pow(lo, n);
			lo = tmp;
		}
		else {							// lo < 0 < up
			double tmp1, tmp2;
			//setMode(FE_UPWARD);
			tmp1 = std::pow(lo, n);
			tmp2 = std::pow(up, n);
			if (tmp1 >= tmp2) {
				up = tmp1;
			}
			else {
				up = tmp2;
			}
			lo = -0.0;
		}
		restoreMode();
	}

	void Interval::exp_assign()
	{
		saveMode();
		throw std::runtime_error("std::exp function is not precise");
		setMode(FE_UPWARD);
		//setMode(FE_DOWNWARD);
		lo = -std::exp(-lo);
		//setMode(FE_UPWARD);
		up = std::exp(up);
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
		if (lo >= 0) {
			printf("Exception: Logarithm of a non-positive number.\n");
			exit(1);
		}
		else {
			throw std::runtime_error("std::exp function is not precise (after 17 digits");
			saveMode();
			//setMode(FE_DOWNWARD);
			setMode(FE_UPWARD);
			lo = -std::log(-lo);
			//setMode(FE_UPWARD);
			up = std::log(up);
			restoreMode();
		}
	}

	double Interval::widthRatio(const Interval& I) const
	{
		double width1, width2, ratio;

		saveMode();
		setMode(FE_UPWARD);
		width1 = up + lo;
		width2 = I.up + I.lo; //switched - to +

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
		sprintf(strTemp, "%.10e", lo);
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
		sprintf(strTemp, "%.10e", up);
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
		fprintf(fp, coefficientFormatCStr, -lo);
		fprintf(fp, " , ");
		//std::fesetround(FE_UPWARD);
		//setMode(FE_TONEAREST);
		fprintf(fp, coefficientFormatCStr, up);

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
		fprintf(fp, coefficientFormatCStr, -lo);
		fprintf(fp, " , ");
		//std::fesetround(FE_UPWARD);
		  //setMode(FE_TONEAREST);
		fprintf(fp, coefficientFormatCStr, up);

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
		lo = temp.getValue_RNDU();
		up = r.getValue_RNDU();
	}

	Interval::Interval(const Real& c, const Real& r)
	{
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		Real temp = Real();
		temp-=c;
		lo =  temp.getValue_RNDU() + r.getValue_RNDU(); //changed RNDD, not sure about that
		//setMode(FE_UPWARD);
		up = c.getValue_RNDU() + r.getValue_RNDU();
		restoreMode();
	}

	Interval::Interval(const Real& l, const Real& u, const int n) //why const int n
	{
		Real temp = Real();
		temp-=l;
		lo = temp.getValue_RNDU();
		up = u.getValue_RNDU();
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
		lo = temp.getValue_RNDU();
		up = r.getValue_RNDU();
	}

	void Interval::sup(Real& u) const
	{
		mpfr_set_d(u.value, up, MPFR_RNDU);
	}

	void Interval::inf(Real& l) const
	{
		//Real temp=Real();
		//temp-=l;
		//mpfr_set_d(temp.value, lo, MPFR_RNDU);
		mpfr_set_d(l.value,-lo,MPFR_RNDD);
		//l.mul_assign_RNDU(-1);
		
	}

	void Interval::midpoint(Real& mid) const
	{
		saveMode();
		setMode(FE_TONEAREST);
		mpfr_set_d(mid.value, (-lo + up) / 2.0, MPFR_RNDN);
		restoreMode();
	} //Not sure how to switch

	void Interval::toCenterForm(Real& center, Real& radius) const
	{
		saveMode();
		setMode(FE_TONEAREST);
		mpfr_set_d(center.value, (-lo + up) / 2.0, MPFR_RNDN);

		setMode(FE_UPWARD);
		mpfr_set_d(radius.value, (up + lo) / 2.0, MPFR_RNDU);
		restoreMode();
	} //Not sure how to switch

	void Interval::bloat(const Real& e)
	{
		saveMode();
		setMode(FE_DOWNWARD);
		lo += e.getValue_RNDU(); //NOT sure if U or D is correct
		setMode(FE_UPWARD);
		up += e.getValue_RNDU(); //see above comment
		restoreMode();
	} //have to double check

	void Interval::mag(Real& m) const
	{
		double tmp1 = fabs(lo), tmp2 = fabs(up);

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
		lo = temp.getValue_RNDU();
		up = r.getValue_RNDU();

		return *this;
	}

	Interval& Interval::operator = (const double d)
	{
		lo = -d;
		up = d;

		return *this;
	}

	Interval& Interval::operator += (const double c)
	{
		saveMode();
		setMode(FE_UPWARD);
		//setMode(FE_DOWNWARD);
		lo -= c;
		//setMode(FE_UPWARD);
		up += c;
		restoreMode();

		return *this;
	}

	Interval& Interval::operator -= (const double c)
	{
		saveMode();
		//setMode(FE_DOWNWARD);
		setMode(FE_UPWARD);
		lo += c;
		//setMode(FE_UPWARD);
		up -= c;
		restoreMode();

		return *this;
	}

	Interval& Interval::operator *= (const double c)
	{
		saveMode();
		setMode(FE_UPWARD);
		if (c >= 0) {
			//setMode(FE_DOWNWARD);
			lo *= c;
			//setMode(FE_UPWARD);
			up *= c;
		}
		else {
			double temp = -lo;
			//setMode(FE_DOWNWARD);
			lo = -up * c;
			//setMode(FE_UPWARD);
			up = temp * c;
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
			lo /= c;
			//setMode(FE_UPWARD);
			up /= c;
		}
		else {
			double temp = -lo;
			//setMode(FE_DOWNWARD);
			lo = -up / c;
			//setMode(FE_UPWARD);
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
		setMode(FE_UPWARD);
		if (c > 0) {
			//setMode(FE_DOWNWARD);
			
			result.lo = lo * c;
			//setMode(FE_UPWARD);
			result.up = up * c;
		}
		else {
			//setMode(FE_DOWNWARD);
			result.lo = -up * c;
			//setMode(FE_UPWARD);
			result.up = -lo * c;
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
			result.lo = lo / c;
			//setMode(FE_UPWARD);
			result.up = up / c;
		}
		else {
			//setMode(FE_DOWNWARD);
			result.lo = -up / c;
			//setMode(FE_UPWARD);
			result.up = -lo / c;
		}
		restoreMode();

		return result;
	}

	
	void Interval::mul_add(Interval* result, const Interval* intVec, const int size)
	{
		double tmp1, tmp2, tmp_up, tmp_lo;

		saveMode();
		setMode(FE_UPWARD);
		if (lo <= 0) //comparing flip
		{
			
			for (int i = 0; i < size; ++i)
			{
				if (intVec[i].lo <= 0) //comparing flip
				{
					
					//setMode(FE_DOWNWARD);
					tmp_lo = -lo * intVec[i].lo;
					//setMode(FE_UPWARD);
					tmp_up = up * intVec[i].up;
				}
				else if (intVec[i].up <= 0)
				{
					//setMode(FE_DOWNWARD);
					
					tmp_lo = up * intVec[i].lo;
					//setMode(FE_UPWARD);
					tmp_up = -lo * intVec[i].up;
				}
				else
				{
					//setMode(FE_DOWNWARD);
					tmp_lo = up * intVec[i].lo;
					//setMode(FE_UPWARD);
					tmp_up = up * intVec[i].up;
				}

				//setMode(FE_DOWNWARD);
				result[i].lo = result[i].lo + tmp_lo;
				//setMode(FE_UPWARD);
				result[i].up = result[i].up + tmp_up;
			}
		}
		else if (up <= 0)
		{
			for (int i = 0; i < size; ++i)
			{
				if (intVec[i].lo <= 0) //comparing flip
				{
					//setMode(FE_DOWNWARD);
					tmp_lo = lo * intVec[i].up;
					//setMode(FE_UPWARD);
					tmp_up =- up * intVec[i].lo;
				}
				else if (intVec[i].up <= 0)
				{
					//setMode(FE_DOWNWARD);
					tmp_lo = -up * intVec[i].up;
					//setMode(FE_UPWARD);
					tmp_up = lo * intVec[i].lo;
				}
				else
				{
					//setMode(FE_DOWNWARD);
					tmp_lo = lo * intVec[i].up;
					//setMode(FE_UPWARD);
					tmp_up = lo * intVec[i].lo;
				}
				//setMode(FE_DOWNWARD);
				result[i].lo = result[i].lo + tmp_lo;
				//setMode(FE_UPWARD);
				result[i].up = result[i].up + tmp_up;
			}
		}
		else
		{
			for (int i = 0; i < size; ++i)
			{
				if (intVec[i].lo >= 0)
				{
					//setMode(FE_DOWNWARD);
					tmp_lo = lo * intVec[i].up;
					//setMode(FE_UPWARD);
					tmp_up = up * intVec[i].up;
				}
				else if (intVec[i].up <= 0)
				{
					//setMode(FE_DOWNWARD);
					tmp_lo = up * intVec[i].lo;
					//setMode(FE_UPWARD);
					tmp_up = lo * intVec[i].lo;
				}
				else
				{
					//setMode(FE_DOWNWARD);
					tmp1 = lo * intVec[i].up;
					tmp2 = up * intVec[i].lo;

					if (tmp1 < tmp2) // flipped sign
					{
						tmp_lo = tmp2;
					}
					else
					{
						tmp_lo = tmp1;
					}

					//setMode(FE_UPWARD);
					tmp1 = lo * intVec[i].lo;
					tmp2 = up * intVec[i].up;

					if (tmp1 > tmp2)
					{
						tmp_up = tmp1;
					}
					else
					{
						tmp_up = tmp2;
					}
				}

				//setMode(FE_DOWNWARD);
				result[i].lo = result[i].lo + tmp_lo;
				//setMode(FE_UPWARD);
				result[i].up = result[i].up + tmp_up;
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
