from PIL import Image
#doc pillow : https://pillow.readthedocs.io/en/stable/reference/Image.html
from datetime import datetime
import os
import numpy as np
from time import time

#moyenne pondérée pour chaque composante rgb
def moyennepixels_ponderee(image):
	red, green, blue = image.split()
	return np.mean(red), np.mean(green), np.mean(blue)

extensions = ['jpg','jpeg',"JPG"]
def initialiseimages():
	print("Initialisation en cours")
	#on met dans un dictionnaire tous les noms des images dont on déjà trouvé la couleur moyenne, avec cette couleur moyenne associée
	database = chemin + "/Photos avec moyennes connues.txt"
	if os.path.exists(database):
		with open(database,"r") as photos_connues:
			texte = photos_connues.read()
		moyenne_pixels_photo = eval(texte)
	else:
		moyenne_pixels_photo = {}

	path = chemin + '/Images'
	compteur = 0
	for root, subdirs, files in os.walk(path):
		for filename in files:
			if filename[filename.rfind('.')+1:] not in extensions:
				continue
			compteur+=1
			if root+"/"+filename in moyenne_pixels_photo.values():
				continue
			# print(root+"/"+filename)
			try:
				photo = Image.open(root+"/"+filename)
			except:
				continue
			rgb = moyennepixels_ponderee(photo) #on trouve leur couleur moyenne et on l'ajoute au dictionnaire
			#on met dans un dictionnaire tous les noms des images dont on déjà trouvé la couleur moyenne, avec cette couleur moyenne associée
			moyenne_pixels_photo[rgb] = root+"/"+filename
			try:#certains noms de fichiers comportent des caractères qui ne peuvent pas être écrits dans le fichier
				with open(chemin + "/Photos avec moyennes connues Test écriture.txt","w") as fichier:
					fichier.write(str({rgb:root+"/"+filename}))
			except:
				del moyenne_pixels_photo[rgb]
				print("Erreur d'écriture", root+"/"+filename)
				continue
			print("Photo {0}".format(compteur))

	with open(chemin + "/Photos avec moyennes connues.txt","w") as fichier:
		fichier.write(str(moyenne_pixels_photo))

	delete = chemin + "/Photos avec moyennes connues Test écriture.txt"
	if os.path.exists(delete):
		os.remove(delete)

	print("Initialisation terminée")

def afficher(objectif,moyenne_pixels_photo,NB_COLONNES,NB_LIGNES,LARGEUR_PHOTOS,HAUTEUR_PHOTOS):
	save_images_resized = {}

	#le portrait est découpé en rectangles, on trouve la couleur moyenne de chaque zone, puis on trouve dans le dict
	#le filename dont la couleur moyenne est la plus proche, et on affiche cette image (redimensionnée) dans le rectangle du portrait.
	debut=time()
	for colonne in range(NB_COLONNES):
		# print("Colonne {0}".format(colonne+1))
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
		actu=time()
		temps_restant = int((actu-debut)/(colonne+1) * (NB_COLONNES-colonne-1))
		heures = temps_restant//3600
		minutes = (temps_restant-heures*3600)//60
		secondes = temps_restant-heures*3600-minutes*60
		print(f"Colonne {colonne+1}. Fin de l'image estimée dans {heures} heure{'s'*max((min(2,heures)-1),0)} {minutes} minute{'s'*max((min(2,minutes)-1),0)} {secondes} seconde{'s'*max((min(2,secondes)-1),0)}")
	# objectif = objectif.crop((0, 0, colonne*LARGEUR_PHOTOS+LARGEUR_PHOTOS, ligne*HAUTEUR_PHOTOS+HAUTEUR_PHOTOS))
	objectif.save(chemin + "/Rendus/"+str(datetime.now()).replace(":","-")[:-7]+" Rendu "+str(NB_COLONNES)+".jpg")



chemin = "C:/Users/OneDrive/Documents/Python/Mosaïque photos/Mosaique-images"
def main():
	Objectif = Image.open(chemin + "/Objectif.jpg")

	initialiseimages()
	resolution = [1,2,3,6,9,12,15,20,25,37,50,70,90,100,125,150,200,250,300,500]
	# resolution = [5,20,50]

	with open(chemin + "/Photos avec moyennes connues.txt","r") as photos_connues:
		texte = photos_connues.read()
	moyenne_pixels_photo = eval(texte)
	numero=-1
	debut = time()
	for i in resolution:
		numero+=1
		NB_LIGNES = NB_COLONNES = i
		print(NB_LIGNES,"x",NB_COLONNES)
		objectif = Objectif.copy()
		LARGEUR_PHOTOS = round(objectif.width/NB_COLONNES)
		HAUTEUR_PHOTOS = round(objectif.height/NB_LIGNES)
		# HAUTEUR_PHOTOS = objectif.height/NB_LIGNES
		# LARGEUR_PHOTOS = objectif.width/NB_COLONNES
		# HAUTEUR_PHOTOS = objectif.height//NB_LIGNES
		# LARGEUR_PHOTOS = objectif.width//NB_COLONNES
		# print(LARGEUR_PHOTOS,objectif.width/NB_COLONNES, HAUTEUR_PHOTOS,objectif.height/NB_LIGNES)
		afficher(objectif,moyenne_pixels_photo,NB_COLONNES,NB_LIGNES,LARGEUR_PHOTOS,HAUTEUR_PHOTOS)
		actu = time()
		temps_restant = int((actu-debut)/sum(resolution[:numero+1]) * sum(resolution[numero+1:]))
		heures = temps_restant//3600
		minutes = (temps_restant-heures*3600)//60
		secondes = temps_restant-heures*3600-minutes*60
		print(f"Fin de toutes les images estimée dans {heures} heure{'s'*max((min(2,heures)-1),0)} {minutes} minute{'s'*max((min(2,minutes)-1),0)} {secondes} seconde{'s'*max((min(2,secondes)-1),0)}")
	
main()