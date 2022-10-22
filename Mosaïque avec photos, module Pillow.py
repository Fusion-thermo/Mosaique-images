from PIL import Image
import glob
from datetime import datetime
#doc pillow : https://pillow.readthedocs.io/en/stable/reference/Image.html

Objectif=Image.open("Objectif.jpg")
pngdict={}
NB_LIGNES=15
NB_COLONNES=15
LARGEUR_PHOTOS=Objectif.width//NB_COLONNES
HAUTEUR_PHOTOS=Objectif.height//NB_LIGNES



#le pixel gardé est le pixel le plus courant dans l'image
def moyennepixels(image,largeur=LARGEUR_PHOTOS,hauteur=HAUTEUR_PHOTOS):
	currentmax=(0,0)
	couleurs={}
	for x in range(largeur):
		for y in range(hauteur):
			rvb=image.getpixel((x,y))
			if rvb in couleurs.keys():
				couleurs[rvb]+=1
				if couleurs[rvb]>currentmax[1]:
					currentmax=(rvb,couleurs[rvb])
			else:
				couleurs[rvb]=0
	return currentmax[0]

#moyenne pondérée pour chaque composante rgb
def moyennepixels_ponderee(image,largeur=LARGEUR_PHOTOS,hauteur=HAUTEUR_PHOTOS):
	red={}
	green={}
	blue={}
	for x in range(largeur):
		for y in range(hauteur):
			rvb=image.getpixel((x,y))
			if rvb[0] in red.keys():
				red[rvb[0]]+=1
			else:
				red[rvb[0]]=1
			if rvb[1] in green.keys():
				green[rvb[1]]+=1
			else:
				green[rvb[1]]=1
			if rvb[2] in blue.keys():
				blue[rvb[2]]+=1
			else:
				blue[rvb[2]]=1
	rouge_num=0
	for i in red.keys():
		rouge_num+=i*red[i]
	rouge=int(rouge_num/sum(red.values()))
	vert_num=0
	for i in green.keys():
		vert_num+=i*green[i]
	vert=int(vert_num/sum(green.values()))
	bleu_num=0
	for i in blue.keys():
		bleu_num+=i*blue[i]
	bleu=int(bleu_num/sum(blue.values()))
	return (rouge,vert,bleu)


def initialiseimages():
	#on met dans un dictionnaire tous les noms des images dont on déjà trouvé la couleur moyenne, avec cette couleur moyenne associée
	try:
		photos_connues=open("Photos avec moyennes connues.txt","r")
		texte=photos_connues.read()
		photos_connues.close()
		separation=texte.split("|")
		separation.pop()
		moyenne_pixels_photo={}
		for i in range(0,len(separation),2):
			moyenne_pixels_photo[separation[i]]=separation[i+1]
	except:
		moyenne_pixels_photo={}


	all_images=glob.glob('Images/*')
	for filename in all_images: #pour toutes les images du dossier source
		#print(filename)
		if filename in moyenne_pixels_photo.keys():#si elles ne sont pas déjà dans la liste susmentionnée
			continue
		photo = Image.open(filename)
		photo=photo.resize((700,500))#on les ouvre et on leur done une résolution plus basse (car photos souvent 5000x3000)
		pngdict[filename] = photo  # référence
		rgb=moyennepixels_ponderee(photo,photo.width,photo.height)#on trouve leur couleur moyenn et on l'ajoute au dictionnaire
		print("Photo {0}".format(all_images.index(filename)))
		moyenne_pixels_photo[filename]=rgb

	photos_connues=open("Photos avec moyennes connues.txt","w")#le dictionnaire écrit les nouvelles photos avec leurs couleurs moyennes
	for nom_fichier in moyenne_pixels_photo.keys():
		photos_connues.write(nom_fichier+"|"+str(moyenne_pixels_photo[nom_fichier])+"|")
	photos_connues.close()

	print("liste initialisée")

def afficher():
	#on met dans un dictionnaire tous les noms des images dont on déjà trouvé la couleur moyenne, avec cette couleur moyenne associée
	moyenne_pixels_photo={}
	photos_connues=open("Photos avec moyennes connues.txt","r")
	texte=photos_connues.read()
	photos_connues.close()
	separation=texte.split("|")
	separation.pop()
	for i in range(0,len(separation),2):
		moyenne_pixels_photo[eval(separation[i+1])]=separation[i]

	#le portrait est découpé en rectangles, on trouve la couleur moyenne de chaque zone, on trouve dans le dict
	#le filename dont la couleur moyenne est la plus proche, et on affiche cette image (redimensionnée) dans le rectangle du portrait.
	for colonne in range(NB_COLONNES):
		print("Colonne {0}".format(colonne))
		for ligne in range(NB_LIGNES):
			box=(colonne*LARGEUR_PHOTOS,ligne*HAUTEUR_PHOTOS,colonne*LARGEUR_PHOTOS+LARGEUR_PHOTOS,ligne*HAUTEUR_PHOTOS+HAUTEUR_PHOTOS)
			region=Objectif.crop(box)
			couleur=moyennepixels_ponderee(region,region.width,region.height)
			min_difference=10**6
			for rgb in moyenne_pixels_photo.keys():
				difference=abs(rgb[0]-couleur[0])+abs(rgb[1]-couleur[1])+abs(rgb[2]-couleur[2])
				if difference<min_difference:
					min_difference=difference
					filename=moyenne_pixels_photo[rgb]
			remplacement_region=Image.open(filename)
			remplacement_region=remplacement_region.resize((LARGEUR_PHOTOS,HAUTEUR_PHOTOS))
			Objectif.paste(remplacement_region,box)
	Objectif.save("Rendus/"+str(datetime.now()).replace(":","-")[:-7]+" Rendu "+str(NB_COLONNES)+".jpg")
	#Objectif.show()

initialiseimages()
resolution=[1,2,3,6,9,12,15,20,25,37,50,70,90,100,125,150]
for i in resolution:
	print(i)
	Objectif=Image.open("Objectif.jpg")
	NB_LIGNES=NB_COLONNES=i
	LARGEUR_PHOTOS=Objectif.width//NB_COLONNES
	HAUTEUR_PHOTOS=Objectif.height//NB_LIGNES
	afficher()