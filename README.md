# Hustle

WARNING!! HUSTLE IS A EXPERIMENTAL LANGUAGE. IT IS NOT COMPLETE.
MANY THINGS HAVE STOPED WORKING WHILE I AM ADDING COMPILATION HUSTLE
NO PROGRAMS THAT WORKED IN THE PAST WILL WORK NOW, 0 PERCENT BACKWARDS COMPATIBILITY FOR NOW
I WILL ADD THE REST OF THE FEATURES FOR COMPILATION MODE AS TIME GOES ON 

This project was writen with its base being the Youtube tutorial [Make YOUR OWN Programming Language](https://www.youtube.com/playlist?list=PLZQftyCk7_SdoVexSmwy_tBgs7P0b97yD) by [CodePulse](https://www.youtube.com/channel/UCUVahoidFA7F3Asfvamrm7w). The only difference is that his language is interpreted while my language is interpreted and compiled to assembly code.
Thanks for his help for the awesome tutorial.

THIS WHOLE THING IS MOSTLY THE WORK THAT WAS DONE BY CODEPULSE 
HE MADE A TUTORIAL AND i JUST FOLLOROWED IT (BY FOLLOWED IT I MEAN CTRL+C AND CTRL+V)
I JUST WANTED TO TELL THAT THANK YOU TO CODEPULSE FOR KINDA GIVING ME A STARTER LANGUAGE TO WORK WITH
I AM JUST GONNA BUILD ON THAT JUST FOR THE INTERPRETER LANGUAGE
FOR THE COMPILED HUSTLE LANGUAGE I WILL USE MY OWN CODEBASE THAT MEANS TO CTRL+C AND CTRL+V
THIS PROJECT IS NOTHING BUT A SMALL PROJECT THAT I AM DOING TO UNDERSTAND LEXING AND PARING
AFTER I AM DONE WITH THAT I WILL BE MAKING THE COMPILED VERSION OF THE LANGUAGE WITHOUT ANY OTHER GUY'S HELP

codepulse's tutorial:- https://www.youtube.com/watch?v=Eythq9848Fg&list=PLZQftyCk7_SdoVexSmwy_tBgs7P0b97yD

# Installation
```console
$ sudo ./install.sh 
```
give your password, and you are done

# Quick Start

```console
$ ./hustle.py help
$ ./hustle.py run examples/fizzbuzz.hsle
$ ./hustle.py com check_asm/foo.hsle (compile mode is still not finished)
```

# MileStones
- [ ] Turing-Complete (our language is soo new that it is not even turing complete yet)
- [ ] Compiled into intermidiate representation (IN PROGRESS)
- [ ] Memory Allocation
- [ ] Stactic Type Checking
- [ ] Optimized 
- [ ] Cross Platform


# Future Plans
- [ ] Switch to fasm instead of nasm
- [ ] Remove interpreter mode (IN PROGRESS)
- [ ] re-write the compiler's lexer and parser
- [ ] Create Documentaion (after completing the compilation mode) 