# DS5001 Text Analysis

## Project Theseus Node Description

Theseus node is a repository containing a graphical word comparator between two corpuses.  Those two corpuses could be two distinct sets, or it can be a large corpus split in half.  The distinction depends on it's use.

At the fundamental function of Theseus node:
* Rank the words in each corpus by frequency
* Create x, y and word mapping lists.  Where for example x[i], y[i], words[i] refers to the x,y coordinates and the word itself.
* From that mapping we can derive some useful interpretations.

## Auto Determining Stop Words
The words that show up along the 45 degree diagonal, and are out further in radius are almost always exclusively stop words.  (Some examples of where this is not true include texts that include IT as in the department, not the pronoun.

The big win here is that you don't have to know the language.  If you are given large corpus of Italian for example (I don't speak Italian), the algorithm would split the text and treat each half as a corpus to compare.  The words along the diagonal end up being the stop words.

## Auto Isolating words for context identification
There are four distinct clusters of words, or rather areas in the graphs.

* The diagonal, 45 degrees.
* Words near the origin with small radius
* Words more distant from radius but along x OR y axis. (two groups)

I already mentioned the stop words.

The group near origin can be discarded, not enough signal to mean much.

The other two groups are words typically related to a topic.  For example comparing a wide random selection of web pages against a corpus of lawyer office web pages yields the vocabulary that identifies a lawyer web page, (pro bono, quid pro quo, etc)


## Aim of the project
My aim of this project is to complete the functionality and add enough graphics to make it useful to help understand the content of a corpus.