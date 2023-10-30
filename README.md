# plouf
Houdini Tools and a python package for a basic pipeline in Solaris

## What is plouf ?
During my final year at ArtFX School on my graduation film "[Firemen](https://www.instagram.com/firemen_shortfilm/)" we decided to use Karma to render our images. So that implied to use some kind of an USD pipeline on top of the school existing 'classic' one.

So Plouf stands for : 

*Pipeline Officieux Uniquement pour Firemen* (Unofficial Pipeline Only for Firemen)

The main goals developing plouf : 
- Work **with** the school pipeline, not against it (so matching the naming convention and folder structure)
- Be **artist friendly** (providing tools to automate and ease technical tasks in Solaris)
- Be kind of **production ready** as quick as possible

So I developed plouf rather quickly to anwser a very specific and targeted need, so in no case it's a meant to work right now on another project. 
The main reason it is here on github is for reference and archive. 
(That said it should kind of work)

## How is plouf ?
plouf is first of all a bunch of Houdini HDAs to publish (save) and load (reference or sublayer) USD files in Solaris. 

Behind it the python package "plouf" powers the hdas and manages naming convention and folder structure.

Other that load & publish nodes you have some various utility nodes that we've used on Firemen, for importing tracking abc from nuke properly, to setup render layers in Karma, etc ...

## Unpacked HDA
Note that all the HDA in this `otls` directory are in an 'unpacked' format. If you want to repack them see :
[Working with files and assets as text](https://www.sidefx.com/docs/houdini/assets/textfiles.html)

## References
[Github repo of ArtFX](https://github.com/ArtFXDev) (You can find the "Silex" pipeline and tools that we used with plouf)
