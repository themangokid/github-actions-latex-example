Scan the project 2 times. Think about how to implement the new text (OT and NT) with the new file format without editing it at all, you can ofc parse but not touch the files yourself. I also want you to do all of the verses that is italic in the files, should 50% alpha so that it is obvious that it is not in Gods word. Think about this 2 times. Since I cannot render the project you have to be very sure of the implementations you are going to do, since I cannot afford to let bugs or layout errors to be included. No notes or references is needed, how ever do not remove, we will look in to that later if so. You should probably do the entire book using the same solution since IF there would be a change I can just parse th DBL file again and just inser the needed change. 

The project is kind of old and has some adhoc solutions. But you cannot remove the TOC, the lettering, you can do what ever you need to do since I have a back up the project. Please program a solution that is using less code. 

The files are incomplete srb_bibeln/gt/Femte_Mosebok as an example. You basically don't need to touch anything like that its just that you have to use the function 
```
\ProcessAndRenderFile{srb_bibeln//psaltaren/psalm18.txt}{Psalm 18}
```
You cannot rewrite that function most likely since it does too much. If you want you can clean every file in the repo since that would make sense. Don't care about the verse numbers. 

This is a kind of advanced system and so you cannot really make any misses, 

I cannot render more than like 10-20 pages so when you are done uncomment that much so I can see what you have done.
Remember that the goal is to use the correct base text, .usx files and ill supply with images of the previous result. 