from PIL import Image
#doc pillow : https://pillow.readthedocs.io/en/stable/reference/Image.html
import glob
from datetime import datetime
import os
from time import time
import numpy as np


#moyenne pondérée pour chaque composante rgb
def moyennepixels_ponderee(image):
	red, green, blue = image.split()
	red, green, blue = np.mean(red), np.mean(green), np.mean(blue)
	return red, green, blue


def initialiseimages():
	#on met dans un dictionnaire tous les noms des images dont on déjà trouvé la couleur moyenne, avec cette couleur moyenne associée
	database = chemin + "/Photos avec moyennes connues.txt"
	if os.path.exists(database):
		with open(database,"r") as photos_connues:
			texte = photos_connues.read()
		moyenne_pixels_photo = eval(texte)
	else:
		moyenne_pixels_photo = {}


	all_images = glob.glob(chemin + '/Images/*')
	compteur = 0
	for filename in all_images: #pour toutes les images du dossier source
		#print(filename)
		compteur+=1
		if filename in moyenne_pixels_photo.values():
			continue
		photo = Image.open(filename)
		#réduire la taille de l'image avant de regarder le rgb moyen raccourcit un peu le temps de calcul mais peu, autant garder la précision
		rgb = moyennepixels_ponderee(photo)#on trouve leur couleur moyenne et on l'ajoute au dictionnaire
		print("Photo {0}".format(compteur))
		moyenne_pixels_photo[rgb] = filename

	#on met dans un dictionnaire tous les noms des images dont on déjà trouvé la couleur moyenne, avec cette couleur moyenne associée
	photos_connues = open(chemin + "/Photos avec moyennes connues.txt","w")#le dictionnaire écrit les nouvelles photos avec leurs couleurs moyennes
	photos_connues.write(str(moyenne_pixels_photo))
	photos_connues.close()

	print("Liste initialisée")

def afficher(objectif):
	moyenne_pixels_photo = {}
	with open(chemin + "/Photos avec moyennes connues.txt","r") as photos_connues:
		texte = photos_connues.read()
	moyenne_pixels_photo = eval(texte)
	save_images_resized = {}

	#le portrait est découpé en rectangles, on trouve la couleur moyenne de chaque zone, on trouve dans le dict
	#le filename dont la couleur moyenne est la plus proche, et on affiche cette image (redimensionnée) dans le rectangle du portrait.
	for colonne in range(NB_COLONNES):
		print("Colonne {0}".format(colonne+1))
		for ligne in range(NB_LIGNES):
			box = (colonne*LARGEUR_PHOTOS,ligne*HAUTEUR_PHOTOS,colonne*LARGEUR_PHOTOS+LARGEUR_PHOTOS,ligne*HAUTEUR_PHOTOS+HAUTEUR_PHOTOS)
			# box = (round(colonne*LARGEUR_PHOTOS), round(ligne*HAUTEUR_PHOTOS), round(colonne*LARGEUR_PHOTOS+LARGEUR_PHOTOS), round(ligne*HAUTEUR_PHOTOS+HAUTEUR_PHOTOS))
			dim_largeur = box[2] - box[0]
			dim_hauteur = box[3] - box[1]
			region = objectif.crop(box)
			couleur = moyennepixels_ponderee(region)
			min_difference = 3 * 256
			for rgb in moyenne_pixels_photo.keys():
				difference = abs(rgb[0]-couleur[0])+abs(rgb[1]-couleur[1])+abs(rgb[2]-couleur[2])
				if difference<min_difference:
					min_difference = difference
					filename = moyenne_pixels_photo[rgb]
			if filename in save_images_resized.keys():
				remplacement_region = save_images_resized[filename]
				#priorité à la vitesse d'exécution, on ne sera pas bon au pixel près à cause des arrondis
				# box = [round(colonne*LARGEUR_PHOTOS), round(ligne*HAUTEUR_PHOTOS), round(colonne*LARGEUR_PHOTOS) + remplacement_region.width, round(ligne*HAUTEUR_PHOTOS) + remplacement_region.height]
			else:
				remplacement_region = Image.open(filename)
				remplacement_region = remplacement_region.resize((dim_largeur,dim_hauteur)) #responsable de plus de 95% du temps de calcul
				save_images_resized[filename] = remplacement_region
			objectif.paste(remplacement_region,box)
	# objectif = objectif.crop((0, 0, colonne*LARGEUR_PHOTOS+LARGEUR_PHOTOS, ligne*HAUTEUR_PHOTOS+HAUTEUR_PHOTOS))
	objectif.save(chemin + "/Rendus/"+str(datetime.now()).replace(":","-")[:-7]+" Rendu "+str(NB_COLONNES)+".jpg")

chemin = "C:/Users/OneDrive/Documents/Python/Mosaïque photos/Mosaique-images"
nom_image = "Objectif.jpg"
Objectif = Image.open(chemin + "/" + nom_image)

initialiseimages()
resolution = [1,2,3,6,9,12,15,20,25,37,50,70,90,100,125,150]
# resolution = [125]
for i in resolution:
	print(i,"x",i)
	NB_LIGNES = NB_COLONNES = i
	objectif = Objectif.copy()
	LARGEUR_PHOTOS = round(objectif.width/NB_COLONNES)
	HAUTEUR_PHOTOS = round(objectif.height/NB_LIGNES)
	# HAUTEUR_PHOTOS = objectif.height/NB_LIGNES
	# LARGEUR_PHOTOS = objectif.width/NB_COLONNES
	# HAUTEUR_PHOTOS = objectif.height//NB_LIGNES
	# LARGEUR_PHOTOS = objectif.width//NB_COLONNES
	print(LARGEUR_PHOTOS,objectif.width/NB_COLONNES, HAUTEUR_PHOTOS,objectif.height/NB_LIGNES)
	afficher(objectif)
