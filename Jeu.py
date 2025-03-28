import pygame
from combattant import Combattant
debug = False # ! pas oublier de changer aussi dans Combattant.py ! 

# Initialisation de Pygame
pygame.init()

manettes_dispo = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

# Si au moins une manette est disponible, on affiche le message
if manettes_dispo:
    print("Manettes détectées :", [manette.get_name() for manette in manettes_dispo])
else:
    print("Pas de manette connectée ! ")
ecran_long = 1400
ecran_larg = 800
ecran = pygame.display.set_mode((ecran_long, ecran_larg))
pygame.display.set_caption("Ratz Fighter")

# Chargement des ressources
titre_img = pygame.image.load("assets/Titre RATZ FIGHTER.png")
titre_img = pygame.transform.scale(titre_img, (1800, 700)) #titre menu et scale en x y 
fd_img = pygame.image.load("assets/fd de niveau.png").convert_alpha() #fd jeu
police_menu = pygame.font.Font("assets/font.ttf", 45) 
police_jeu = pygame.font.Font("assets/font.ttf", 30) #juste pour taille
police_decompte = pygame.font.Font("assets/font.ttf", 60) 

pygame.mixer.music.load("assets/intro.mp3")#que menu
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(1) # Lit la musique d'intro une fois

# Définition des boutons
Bouton_Play = pygame.Rect(610, 355, 180, 50)#X,Y, Longueur, Largeur
Bouton_options = pygame.Rect(545, 460, 310, 50)
Bouton_exit = pygame.Rect(545, 570, 310, 50)
boutton_ok = pygame.mixer.Sound("assets/menuok.wav") 
boutton_annu = pygame.mixer.Sound("assets/menuannule.wav")
intro_cpt = 0
der_cpt_maj = pygame.time.get_ticks()
score = [0, 0]
round_fini = False
round_fini_cooldown = 1000 #! Pas 3sec sinon - de temps au compteur !

# Variables de jeu
jeu_en_cours = True
tmps = pygame.time.Clock() #crée une horloge dans le corps du programme
FPS = 60 #Frame Per Second (Img/sec)
crtl_j1 = "Clavier"
crtl_j2 = "Clavier"


def gerer_musique(action, piste=None, boucle=-1):
    """Gère la musique en fonction de l'état de la variable `musique_active`.

    Paramètres:
    action (str): Peut être "jouer", "pause", "stop", ou "reprendre".
    piste (str): Chemin de la piste à jouer, si applicable.
    boucle (int): Nombre de répétitions pour la lecture de la musique (-1 pour une boucle infinie).
    """
    global musique_active

    if action == "jouer" and musique_active:
        pygame.mixer.music.load(piste)
        pygame.mixer.music.play(boucle)
    elif action == "pause":
        pygame.mixer.music.pause()
    elif action == "stop":
        pygame.mixer.music.stop()
    elif action == "reprendre" and musique_active:
        pygame.mixer.music.unpause()

def Menu():
    """
    Affiche et gère le menu principal du jeu.
    Cette fonction gère la boucle du menu principal, où l'utilisateur peut interagir
    avec les boutons "Jouer", "Options" et "Quitter". Elle traite les événements utilisateur,
    met à jour l'affichage et effectue des transitions vers d'autres parties du jeu
    en fonction de la sélection de l'utilisateur.
    Variables globales :
        jeu_en_cours (bool): Indique si le jeu est en cours d'exécution.
    Actions des boutons :
        - "Jouer" : Lance le jeu en arrêtant la musique actuelle, en jouant la musique
          du niveau et en appelant la fonction `Jeu`.
        - "Options" : Ouvre le menu des options en appelant la fonction `Options`.
        - "Quitter" : Quitte le jeu.
    """
    global jeu_en_cours

    while jeu_en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                jeu_en_cours = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if Bouton_Play.collidepoint(event.pos):  # Si le clic est sur le bouton "Jouer"
                        boutton_ok.play()
                        gerer_musique("stop")
                        gerer_musique("jouer", "assets/Musique niveau.mp3", -1)
                        Jeu()  # Joue la nouvelle musique en boucle
                    elif Bouton_options.collidepoint(event.pos):
                        boutton_ok.play()
                        Options()
                    elif Bouton_exit.collidepoint(event.pos):
                        jeu_en_cours = False
                        boutton_ok.play()
        if debug:
            pygame.draw.rect(ecran, "red", Bouton_Play,2)
            pygame.draw.rect(ecran, "red", Bouton_options,2)
            pygame.draw.rect(ecran, "red", Bouton_exit,2)
        x = (ecran_long - titre_img.get_width()) // 2 + 45 #! Pas confondre aevc les persos !(galère)
        y = (ecran_larg - titre_img.get_height()) // 2 - 110
        ecran.blit(titre_img, (x,y))
        play_txt = police_menu.render("Play", True, (255, 255, 255))
        ecran.blit(play_txt, (610, 355))
        options_txt = police_menu.render("Options", True, (255, 255, 255))
        ecran.blit(options_txt, (545, 460))
        quitter_txt = police_menu.render("Quitter", True, (255, 255, 255))
        ecran.blit(quitter_txt, (545, 570))
        pygame.display.flip()#Met à jour la surface d'affichage complète à l'écran
        #blit = dessiner une image sur une autre


musique_active = True
def Options():
    """
    Affiche et gère le menu "Options".
    Permet de changer les contrôles des joueurs (Clavier/Manette), activer/désactiver
    la musique et revenir au menu précédent. Affiche les boutons et gère les clics.
    """
    global jeu_en_cours, crtl_j1, crtl_j2, musique_active

    bouton_retour = pygame.Rect(30, 30, 275, 45)
    bouton_j1_toggle = pygame.Rect(220, 300, 310, 50)  # Bouton pour basculer Joueur 1
    bouton_j2_toggle = pygame.Rect(220, 500, 310, 50)  # Bouton pour basculer Joueur 2
    bouton_musique = pygame.Rect(450, 600, 500, 50)  # Bouton pour basculer la musique

    while jeu_en_cours:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                jeu_en_cours = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if bouton_retour.collidepoint(event.pos):
                        boutton_annu.play()
                        ecran.fill((0, 0, 0))
                        return
                    elif bouton_j1_toggle.collidepoint(event.pos):
                        # Alterne entre "Clavier" et "Manette" pour Joueur 1
                        crtl_j1 = "Manette" if crtl_j1 == "Clavier" else "Clavier"
                        boutton_ok.play()
                    elif bouton_j2_toggle.collidepoint(event.pos):
                        # Alterne entre "Clavier" et "Manette" pour Joueur 2
                        crtl_j2 = "Manette" if crtl_j2 == "Clavier" else "Clavier"
                        boutton_ok.play()
                    elif bouton_musique.collidepoint(event.pos):
                        musique_active = not musique_active
                        if musique_active:
                            gerer_musique("reprendre")
                            boutton_ok.play()
                        else:
                            gerer_musique("pause")
                            boutton_ok.play()
        ecran.fill((0, 0, 0))
        
        if debug:
            pygame.draw.rect(ecran, "red", bouton_j1_toggle, 2)
            pygame.draw.rect(ecran, "red", bouton_j2_toggle, 2)
            pygame.draw.rect(ecran, "red", bouton_retour, 2)
            pygame.draw.rect(ecran, "red", bouton_musique, 2)

        # Titre Options
        options_titre = police_menu.render("Options", True, (255, 255, 255))
        ecran.blit(options_titre, (520, 100))

        # Bouton Retour
        retour_txt = police_menu.render("Retour", True, (255, 255, 255))
        ecran.blit(retour_txt, (30, 30))

        # Contrôles Joueur 1
        ecran.blit(police_menu.render(f"Joueur 1 : {crtl_j1}", True, (255, 255, 255)), (200, 250))
        toggle_j1_txt = police_menu.render("Changer", True, (255, 255, 255))
        ecran.blit(toggle_j1_txt, (220, 300))

        # Contrôles Joueur 2
        ecran.blit(police_menu.render(f"Joueur 2 : {crtl_j2}", True, (255, 255, 255)), (200, 450))
        toggle_j2_txt = police_menu.render("Changer", True, (255, 255, 255))
        ecran.blit(toggle_j2_txt, (220, 500))

        # Bouton Musique avec état actuel
        texte_musique = "Musique: ON" if musique_active else "Musique: OFF"
        musique_txt = police_menu.render(texte_musique, True, (255, 255, 255))
        ecran.blit(musique_txt, (450, 600))

        pygame.display.flip()


def Menu_Pause():
    global jeu_en_cours
    pygame.mixer.music.pause()
    son_pause = pygame.mixer.Sound("assets/pause.wav")  # Charge l'effet sonore
    son_pause.play()

    bouton_reprendre = pygame.Rect(500, 350, 400, 50)
    bouton_options = pygame.Rect(545, 460, 310, 50)
    bouton_quitter = pygame.Rect(545, 570, 310, 50)
    
      # Joue l'effet sonore  # Met en pause la musique
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    son_pause.play() # Si la touche "Échap" est enfoncée, reprendre le jeu
                    pygame.mixer.music.unpause() 
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN: #si il clique 
                if event.button == 1: # Si le clic est le clic gauche
                    if bouton_reprendre.collidepoint(event.pos):
                        boutton_annu.play()
                        pygame.mixer.music.unpause()
                        return
                    elif bouton_options.collidepoint(event.pos):
                        boutton_ok.play()
                        Options()
                    elif bouton_quitter.collidepoint(event.pos):
                        pygame.quit()
            

        # Affichage du menu pause
        if debug : 
            pygame.draw.rect(ecran, "red", bouton_reprendre,2)
            pygame.draw.rect(ecran, "red", bouton_options,2)
            pygame.draw.rect(ecran, "red", bouton_quitter,2)
        ecran.fill((0, 0, 0))
        pause_texte = police_menu.render("Pause", True, (255, 255, 255))
        ecran.blit(pause_texte, (590,200))
        reprendre_bouton = police_menu.render("Reprendre",True,(255,255,255))
        #pygame.draw.rect(ecran, "red", bouton_reprendre)
        ecran.blit(reprendre_bouton, (500, 350))

        options_texte = police_menu.render("Options", True, (255, 255, 255))
        #pygame.draw.rect(ecran, "red", bouton_options)
        ecran.blit(options_texte, (545, 460))

        exit_texte = police_menu.render("Quitter", True, (255, 255, 255))
        #pygame.draw.rect(ecran, "red", bouton_quitter)
        ecran.blit(exit_texte, (545, 570))
        if debug : 
            pygame.draw.rect(ecran, "red", bouton_reprendre,2)
            pygame.draw.rect(ecran, "red", bouton_options,2)
            pygame.draw.rect(ecran, "red", bouton_quitter,2)
        
        pygame.display.update()
        tmps.tick(15)  # Limite le FPS pour réduire l'utilisation du processeur

def afficher_texte_degrade(surface, texte, police, position, couleur1, couleur2, decalage=5):
    """
    Affiche un texte avec un effet de dégradé (ombrage).

    Paramètres:
    surface (pygame.Surface): La surface où afficher le texte.
    texte (str): Le texte à afficher.
    police (pygame.font.Font): La police du texte.
    position (tuple): Position (x, y) du texte.
    couleur1 (tuple): Couleur de l'ombre (R, G, B).
    couleur2 (tuple): Couleur du texte principal (R, G, B).
    decalage (int): Déplacement de l'ombre.
    """
    ombre = police.render(texte, True, couleur1)
    texte_principal = police.render(texte, True, couleur2)
    surface.blit(ombre, (position[0] + decalage, position[1] + decalage))
    surface.blit(texte_principal, position)


def dessin_fond(ecran, fd_img):
    """
    Dessine le fond du niveau et le recadre correctement en fonction de la fenetre

    Parameters:
    ecran (pygame.ecran): la ecran dans laquelle on insère l'image ou autre élément
    fd_img (pygame.ecran): (Fond_image) sert juste a mettre l'image sélectionné

    """
    recad_fd = pygame.transform.scale(fd_img, (1400, 800)) #recadre par échelle l'mg par fenetre
    ecran.blit(recad_fd, (0, 0))#update de l'ecran
    

def des_barre_vie(ecran, sante, x, y):
    ratio = sante / 100
    pygame.draw.rect(ecran, "white", (x - 2, y - 2, 544, 48))
    pygame.draw.rect(ecran, (218, 32, 46), (x, y, 540, 45))
    pygame.draw.rect(ecran, (57, 178, 81), (x, y, 540 * ratio, 45))

    afficher_texte_degrade(ecran, f"Joueur 1: {score[0]}", police_jeu, (13, 15), (0, 0, 0), (255, 255, 255))
    afficher_texte_degrade(ecran, f"Joueur 2: {score[1]}", police_jeu, (1059, 15), (0, 0, 0), (255, 255, 255))


def txt_info(texte,x,y):
    """
    Affiche le décompte au début des rounds

    Paramètres:
    texte (str): Le texte à afficher
    x (int)
    y (int)
    """
    dec = police_decompte.render(texte, True, (255, 255, 255))
    ecran.blit(dec, (x,y))


def Jeu():
    global jeu_en_cours, intro_cpt, der_cpt_maj, round_fini,crtl_j1, crtl_j2

    der_cpt_maj = pygame.time.get_ticks()
    joueur_1 = Combattant(1, 200, 460)
    joueur_2 = Combattant(2, 1100, 460)

    while jeu_en_cours:
        tmps.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                jeu_en_cours = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    Menu_Pause()

        dessin_fond(ecran, fd_img)
        des_barre_vie(ecran, joueur_1.sante, 10, 50)
        des_barre_vie(ecran, joueur_2.sante, 845, 50)

        if intro_cpt <= 0:
            joueur_1.update()
            joueur_2.update()
            joueur_1.Mouv(ecran_long, ecran_larg, ecran, joueur_2, crtl_j1)
            joueur_2.Mouv(ecran_long, ecran_larg, ecran, joueur_1, crtl_j2)
        else:
            txt_info(str(intro_cpt), 680,200)
            if (pygame.time.get_ticks() - der_cpt_maj) >= 1000:
                intro_cpt -= 1
                der_cpt_maj = pygame.time.get_ticks()

        joueur_1.des(ecran)
        joueur_2.des(ecran)

        
        if debug:
            joueur_1.afficher_info(ecran)
            joueur_2.afficher_info(ecran)

        if round_fini:
            if (pygame.time.get_ticks() - round_fini_cooldown) >= 3000:
                round_fini = False
                intro_cpt = 4 #+1 à mettre
                joueur_1 = Combattant(1, 200, 450)
                joueur_2 = Combattant(2, 1100, 450)
            if joueur_1.est_mort():
                msg_victoire = police_jeu.render("Joueur 2 a gagné !", True, (255, 255, 255))
                ecran.blit(msg_victoire, (ecran_larg / 2, ecran_long / 6))
            if joueur_2.est_mort():
                msg_victoire = police_jeu.render("Joueur 1 a gagné !", True, (255, 255, 255))
                ecran.blit(msg_victoire, (ecran_larg / 2, ecran_long / 6))

        if not round_fini:
            if joueur_1.est_mort():
                score[1] += 1
                round_fini = True
                round_fini_cooldown = pygame.time.get_ticks()
            elif joueur_2.est_mort():
                score[0] += 1
                round_fini = True
                round_fini_cooldown = pygame.time.get_ticks()

        pygame.display.update()
    pygame.quit()
    
Menu()
pygame.quit()
