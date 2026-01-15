# PyDominoPDF

A simple Python script that generates printable fidicuals used by the [Shaper Origin CNC router](https://www.shapertools.com/en-us/). This project is not affiliated with Shaper Tools.

A domino is defined by
   - two rows
   - eight columns
   - the first and last columns are always set

### Procedure

 - Generate bitstrings from numbers between 0 and 4095
 - Each bitstring 001010010111 is divided in the middle (001010 010111). 
   - The first section will be the first row,
   - The second part will be the second row. 
 - The method only works with max. 12 bits (up to 4095) 
 - This will give a maximum of 452 dominos when the follwing rules for valid numbers are applied:
   - The number binary value must have a Hamming weight of exactly 6. This garantees 6 pips of the domino.
   - The two parts of the bitstring must not be mirrored such as 011011 110110.
   - A reversed bitstring must not be seen before in the detected valid ones

### Example

Note that first and last columns are always set.

- when integer value is 2827 => bitstring is 101100000111 => the domino will be:

       11011001 
       10001111
- when integer value is 0663 => bitstring is 001010010111 => the domino will be:
    
       10010101
       10101111

## Prerequisites

Use Python >= 3.8

### pyDominoPDF.py
Local/stand-alone generator that requires the PyX and Bitstring libraries.

### pyDominoValueGenerator.py
Generates a list of valid values used by pyDominoPDF. Requires the Bitstring library.

### index.py
A flask web application for a web hosted version of pyDominoPDF.

## License

This project is licensed under the GPLv3 License - see the [LICENSE](LICENSE) file for details
