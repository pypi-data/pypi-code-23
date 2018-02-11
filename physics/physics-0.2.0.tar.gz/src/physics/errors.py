class Errors:

    """
    The errors class is used to define
    a number with an absolute, relative or
    percentage error and do arithmetic
    operations with them.
    """

    def __init__(self, number, **errors):
        """
        It initializes the object, checks
        if an absolute, relative or percentage is
        given and if not it generates an absolute
        error following the established rules during
        physics conventions.
        """
        self.number = number
        if 'absolute_error' in errors:
            self.absolute_error = errors['absolute_error']
            self.relative_error = errors['absolute_error'] / number
            self.percentage_error = round(
                errors['absolute_error'] / number,
                4) * 100

        elif 'relative_error' in errors:
            self.absolute_error = errors['relative_error'] * number
            self.relative_error = errors['relative_error']
            self.percentage_error = errors['relative_error'] * 100

        elif 'percentage_error' in errors:
            self.absolute_error = (errors['percentage_error'] / 100) * error
            self.relative_error = errors['percentage_error'] / 100
            self.percentage_error = errors['percentage_error']

        else:
            index = 0
            if int(number) is 0 or int(number) is -0:
                index = 0
                list_number = list(str(number - int(number))[2:])
                for i in list_number:
                    list_number[index] = '0'
                    index += 1
                list_number[-1] = '1'
                del index
                self.absolute_error = float('0.' + (''.join(list_number)))
            else:
                self.absolute_error = 1
            self.relative_error = self.absolute_error / number
            self.percentage_error = round(self.relative_error, 4) * 100

    def __radd__(self, second_number):
        """
        That function is used to
        estabilish the result of
        a Reverse Addition, summing
        absolute errors and numbers.
        """
        if isinstance(second_number, errors):
            return errors(self.number + second_number.number,
                          absolute_error=(self.absolute_error +
                                          second_number.absolute_error))
        else:
            return errors(self.number + second_number,
                          absolute_error=self.absolute_error)

    def __iadd__(self, second_number):
        """
        That function is used to
        estabilish the result of
        an Inline Addition, summing
        absolute errors and numbers.
        """
        if isinstance(second_number, errors):
            return errors(self.number + second_number.number,
                          absolute_error=(self.absolute_error +
                                          second_number.absolute_error))
        else:
            return errors(self.number + second_number,
                          absolute_error=self.absolute_error)

    def __add__(self, second_number):
        """
        That function is used to
        estabilish the result of
        an Addition, summing
        absolute errors and numbers.
        """
        if isinstance(second_number, errors):
            return errors(self.number + second_number.number,
                          absolute_error=(self.absolute_error +
                                          second_number.absolute_error))
        else:
            return errors(self.number + second_number,
                          absolute_error=self.absolute_error)

    def __sub__(self, second_number):
        """
        That function is used to
        estabilish the result of
        a Subtraction, summing
        absolute errors and
        subtracting numbers.
        """
        if isinstance(second_number, errors):
            return errors(self.number - second_number.number,
                          absolute_error=(self.absolute_error +
                                          second_number.absolute_error))
        else:
            return errors(self.number - second_number,
                          absolute_error=self.absolute_error)

    def __rsub__(self, second_number):
        """
        That function is used to
        estabilish the result of
        a Reverse Subtraction,
        summing absolute errors
        and subtracting numbers.
        """
        if isinstance(second_number, errors):
            return errors(self.number - second_number.number,
                          absolute_error=(self.absolute_error +
                                          second_number.absolute_error))
        else:
            return errors(self.number - second_number,
                          absolute_error=self.absolute_error)

    def __isub__(self, second_number):
        """
        That function is used to
        estabilish the result of
        an Inline Subtraction,
        summing absolute errors
        and subtracting numbers.
        """
        if isinstance(second_number, errors):
            return errors(self.number - second_number.number,
                          absolute_error=(self.absolute_error +
                                          second_number.absolute_error))
        else:
            return errors(self.number - second_number,
                          absolute_error=self.absolute_error)

    def __mul__(self, second_number):
        """
        That function is used to
        estabilish the result of
        a Multiplication,
        summing relative errors
        and multiplicating numbers.
        """
        if isinstance(second_number, errors):
            return errors(self.number * second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return errors(self.number * second_number,
                          relative_error=self.relative_error)

    def __rmul__(self, second_number):
        """
        That function is used to
        estabilish the result of
        a Reverse Multiplication,
        summing relative errors
        and multiplicating numbers.
        """
        if isinstance(second_number, errors):
            return errors(self.number * second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return errors(self.number * second_number,
                          relative_error=self.relative_error)

    def __imul__(self, second_number):
        """
        That function is used to
        estabilish the result of
        an Inline Multiplication,
        summing relative errors
        and multiplicating numbers.
        """
        if isinstance(second_number, errors):
            return errors(self.number * second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return errors(self.number * second_number,
                          relative_error=self.relative_error)

    def __truediv__(self, second_number):
        """
        That function is used to
        estabilish the result of
        a True Division,
        summing relative errors
        and dividing numbers.
        """
        if isinstance(second_number, errors):
            return errors(self.number / second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return errors(self.number / second_number,
                          relative_error=self.relative_error)

    def __rtruediv__(self, second_number):
        """
        That function is used to
        estabilish the result of
        a Reverse True Division,
        summing relative errors
        and dividing numbers.
        """
        if isinstance(second_number, errors):
            return errors(self.number / second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return errors(self.number / second_number,
                          relative_error=self.relative_error)

    def __itruediv__(self, second_number):
        """
        That function is used to
        estabilish the result of
        an Inline True Division,
        summing relative errors
        and dividing numbers.
        """
        if isinstance(second_number, errors):
            return errors(self.number / second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return errors(self.number / second_number,
                          relative_error=self.relative_error)

    def __floordiv__(self, second_number):
        """
        That function is used to
        estabilish the result of
        a Floor Division,
        summing relative errors
        and dividing numbers.
        """
        if isinstance(second_number, errors):
            return errors(self.number // second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return errors(self.number // second_number,
                          relative_error=self.relative_error)

    def __rfloordiv__(self, second_number):
        """
        That function is used to
        estabilish the result of
        a Reverse Floor Division,
        summing relative errors
        and dividing numbers.
        """
        if isinstance(second_number, errors):
            return errors(self.number // second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return errors(self.number // second_number,
                          relative_error=self.relative_error)

    def __ifloordiv__(self, second_number):
        """
        That function is used to
        estabilish the result of
        an Inline Floor Division,
        summing relative errors
        and dividing numbers.
        """
        if isinstance(second_number, errors):
            return errors(self.number // second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return errors(self.number // second_number,
                          relative_error=self.relative_error)

    def __mod__(self, second_number):
        """
        That function is used to
        estabilish the result of
        a Modulo,
        summing relative errors
        and giving the remainder of
        the divided numbers.
        """
        if isinstance(second_number, errors):
            return errors(self.number % second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return errors(self.number % second_number,
                          relative_error=self.relative_error)

    def __rmod__(self, second_number):
        """
        That function is used to
        estabilish the result of
        a Reverse Modulo,
        summing relative errors
        and giving the remainder of
        the divided numbers.
        """
        if isinstance(second_number, errors):
            return errors(self.number % second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return errors(self.number % second_number,
                          relative_error=self.relative_error)

    def __imod__(self, second_number):
        """
        That function is used to
        estabilish the result of
        an Inline Modulo,
        summing relative errors
        and giving the remainder of
        the divided numbers.
        """
        if isinstance(second_number, errors):
            return errors(self.number % second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return errors(self.number % second_number,
                          relative_error=self.relative_error)

    def __pow__(self, second_number, modulo=0):
        """
        That function is used to
        estabilish the result of
        an Exponentiation,
        multiplicating the first
        relative error for the second
        number and giving arithmetic power.
        """
        if isinstance(second_number, errors):
            if modulo is 0:
                return errors(self.number ** second_number.number,
                              relative_error=(self.relative_error *
                                              second_number.number))
            else:
                return errors((self.number ** second_number.number) %
                              modulo, relative_error=(self.relative_error *
                                                      second_number.number))
        else:
            if modulo is 0:
                return errors(self.number ** second_number,
                              relative_error=(self.relative_error *
                                              second_number))
            else:
                return errors((self.number ** second_number) %
                              modulo, relative_error=(self.relative_error *
                                                      second_number))

    def __rpow__(self, second_number, modulo=0):
        """
        That function is used to
        estabilish the result of
        a Reverse Exponentiation,
        multiplicating the first
        relative error for the second
        number and giving arithmetic power.
        """
        if isinstance(second_number, errors):
            if modulo is 0:
                return errors(self.number ** second_number.number,
                              relative_error=(self.relative_error *
                                              second_number.number))
            else:
                return errors((self.number ** second_number.number) %
                              modulo, relative_error=(self.relative_error *
                                                      second_number.number))
        else:
            if modulo is 0:
                return errors(self.number ** second_number,
                              relative_error=(self.relative_error *
                                              second_number))
            else:
                return errors((self.number ** second_number) %
                              modulo, relative_error=(self.relative_error *
                                                      second_number))

    def __ipow__(self, second_number, modulo=0):
        """
        That function is used to
        estabilish the result of
        an Inline Exponentiation,
        multiplicating the first
        relative error for the second
        number and giving arithmetic power.
        """
        if isinstance(second_number, errors):
            if modulo is 0:
                return errors(self.number ** second_number.number,
                              relative_error=(self.relative_error *
                                              second_number.number))
            else:
                return errors((self.number ** second_number.number) %
                              modulo, relative_error=(self.relative_error *
                                                      second_number.number))
        else:
            if modulo is 0:
                return errors(self.number ** second_number,
                              relative_error=(self.relative_error *
                                              second_number))
            else:
                return errors((self.number ** second_number) %
                              modulo, relative_error=(self.relative_error *
                                                      second_number))

    def __abs__(self):
        """
        That function is used to
        return the absolute value
        of the chosen number.
        """
        return abs(self.number)

    def __neg__(self):
        """
        That function is used to
        return the negative value
        of the chosen number.
        """
        return -(abs(self.number))

    def __pos__(self):
        """
        That function is used to
        return the positive value
        of the chosen number.
        """
        return abs(self.number)

    def __invert__(self):
        """
        That function is used to
        return the inverted value
        of the chosen number.
        """
        return ~self.number

    def __len__(self):
        """
        That function is used to
        return the number of
        digits of the
        chosen number.
        """
        return len(str(self.number))

    def __lt__(self, second_number):
        """
        That function is used to
        compare two numbers
        using "<".
        """
        if isinstance(second_number, errors):
            if (self.percentage_error < second_number.percentage_error):
                return True
            else:
                return False
        else:
            return self < errors(second_number)

    def __le__(self, second_number):
        """
        That function is used to
        compare two numbers
        using "<=".
        """
        if isinstance(second_number, errors):
            if (self.percentage_error <= second_number.percentage_error):
                return True
            else:
                return False
        else:
            return self <= errors(second_number)

    def __eq__(self, second_number):
        """
        That function is used to
        compare two numbers
        using "==".
        """
        if isinstance(second_number, errors):
            if (self.relative_error ==
                second_number.relative_error) and (self.number ==
                                                   second_number.number):
                return True
            else:
                return False
        else:
            return self == errors(second_number)

    def __ne__(self, second_number):
        """
        That function is used to
        compare two numbers
        using "!=".
        """
        if isinstance(second_number, errors):
            if (self.relative_error !=
                second_number.relative_error) and (self.number !=
                                                   second_number.number):
                return True
            else:
                return False
        else:
            return self != errors(second_number)

    def __gt__(self, second_number):
        """
        That function is used to
        compare two numbers
        using ">".
        """
        if isinstance(second_number, errors):
            if (self.percentage_error > second_number.percentage_error):
                return True
            else:
                return False
        else:
            return self > errors(second_number)

    def __ge__(self, second_number):
        """
        That function is used to
        compare two numbers
        using ">=".
        """
        if isinstance(second_number, errors):
            if (self.percentage_error >= second_number.percentage_error):
                return True
            else:
                return False
        else:
            return self >= errors(second_number)

    def __int__(self):
        """
        That function is used to
        return the integer
        of the chosen number.
        """
        return self.number

    def __str__(self):
        """
        That function is used to
        return a string rappresentation
        of the chosen number.
        """
        return (str(self.number) + " ± " + str(self.absolute_error))

    def __float__(self):
        """
        That function is used to
        return the float
        of the chosen number.
        """
        return float(self.number)

    def __round__(self, digits=0):
        """
        That function is used to
        round the chosen number.
        """
        return round(self.number, digits)
