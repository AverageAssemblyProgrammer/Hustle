# Hustle

##This Project has been discontinued

WARNING!! HUSTLE IS A EXPERIMENTAL LANGUAGE. IT IS NOT COMPLETE.
MANY THINGS HAVE STOPED WORKING WHILE I AM ADDING COMPILATION HUSTLE
NO PROGRAMS THAT WORKED IN THE PAST WILL WORK NOW, 0 PERCENT BACKWARDS COMPATIBILITY FOR NOW
I WILL ADD THE REST OF THE FEATURES FOR COMPILATION MODE AS TIME GOES ON 

This project was writen with its base being the Youtube tutorial [Make YOUR OWN Programming Language](https://www.youtube.com/playlist?list=PLZQftyCk7_SdoVexSmwy_tBgs7P0b97yD) by [CodePulse](https://www.youtube.com/channel/UCUVahoidFA7F3Asfvamrm7w). The only difference is that his language is interpreted while my language is interpreted and compiled to assembly code.
Thanks for his help for the awesome tutorial.
codepulse's tutorial:- https://www.youtube.com/watch?v=Eythq9848Fg&list=PLZQftyCk7_SdoVexSmwy_tBgs7P0b97yD

for future me: to fix the structure of the compilation (if statement) deleat the compilation to nasm section of the new codebase and re-write it. (remember to check the lexer for errors

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
