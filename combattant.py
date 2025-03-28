import pygame

debug = False  # ! pas oublier de changer aussi dans jeu.py !

class Combattant:
    def __init__(self, joueur, x, y):
        self.joueur = joueur
        self.rect = pygame.Rect((x, y, 140, 200))  # hitbox du perso
        self.velo_y = 0  # saut y
        self.saut = False
        self.attaquer = False
        self.type_attaque = 0  # pour les animations
        self.sante = 100
        self.der_tmp_combat = 0
        self.attaque_cooldown = 150
        self.en_vie = True
        self.direction = 1 if joueur == 1 else -1
        self.idle_image = pygame.image.load(f"assets/Rat {self.joueur}/rat_{self.joueur} idle.png").convert_alpha()
        self.coup_de_poing = pygame.image.load(f"assets/Rat {self.joueur}/rat_{self.joueur} coup de poing.png").convert_alpha()
        self.coup_de_pied = pygame.image.load(f"assets/Rat {self.joueur}/rat_{self.joueur} coup de pied.png").convert_alpha()
        self.coup_de_queue = pygame.image.load(f"assets/Rat {self.joueur}/rat_{self.joueur} coup de queue.png").convert_alpha()
        self.image_mort = pygame.image.load(f"assets/Rat {self.joueur}/rat_{self.joueur} mort.png").convert_alpha()
        self.image_saut = pygame.image.load(f"assets/Rat {self.joueur}/rat_{self.joueur} saut.png").convert_alpha()
        self.image = self.idle_image

    def Mouv(self, ecran_long, ecran_larg, surface, cible, controle):
        """
        Gère la logique de mouvement et de combat du combattant.

        Paramètres:
        ecran_long (int) : La longueur de l'écran de jeu.
        ecran_larg (int) : La largeur de l'écran de jeu.
        surface (pygame.Surface) : La surface de l'écran de jeu.
        cible (Combattant) : L'adversaire combattant.
        controle (str) : Le type de contrôle utilisé ("Clavier" ou "Manette").
        """
        if self.sante <= 0:
            return  # Si le personnage est mort, ne pas exécuter le reste de la méthode

        vitesse = 10  # Vitesse de déplacement
        dirx = 0  # Direction horizontale
        diry = 0  # Direction verticale
        gravite = 1.8  # Gravité appliquée lors des sauts
        zone_morte = 0.2  # Taille de la zone morte pour les joysticks

        if controle == "Clavier":
            # Gestion des contrôles clavier
            touche = pygame.key.get_pressed()  # Récupére les touches pressées
            if not self.attaquer:
                if self.joueur == 1:
                    # Contrôles pour le joueur 1
                    if touche[pygame.K_q]:
                        dirx = -vitesse  # Déplacement a gauche
                        self.direction = -1  # Changer la direction vers la gauche
                    if touche[pygame.K_d]:
                        dirx = vitesse  # Déplacement vers la droite
                        self.direction = 1  # Changer la direction vers la droite

                    if touche[pygame.K_z] and not self.saut:
                        self.velo_y = -30  # Début du saut
                        self.saut = True  # Indiquer que le personnage saute
                    if touche[pygame.K_a] and not self.attaquer:
                        self.attaquer = True
                        self.attaque(surface, cible, 5)  # Coup de poing : 5 dégâts
                        self.der_tmp_combat = pygame.time.get_ticks()  # Enregistre le temps de l'attaque
                        self.type_attaque = 1  # Coup de poing
                    if touche[pygame.K_e] and not self.attaquer:
                        self.attaquer = True
                        self.attaque(surface, cible, 10)  # Coup de pied : 10 dégâts
                        self.der_tmp_combat = pygame.time.get_ticks()  # Enregistrer le temps de l'attaque
                        self.type_attaque = 2  # Coup de pied
                    if touche[pygame.K_r] and not self.attaquer:
                        self.attaquer = True
                        self.attaque(surface, cible, 20)  # Coup de queue : 20 dégâts
                        self.der_tmp_combat = pygame.time.get_ticks()
                        self.type_attaque = 3  # Coup de queue

                if self.joueur == 2:
                    # Contrôles pour le joueur 2
                    if touche[pygame.K_LEFT]:
                        dirx = -vitesse
                        self.direction = -1
                    if touche[pygame.K_RIGHT]:
                        dirx = vitesse
                        self.direction = 1
                    if touche[pygame.K_UP] and not self.saut:
                        self.velo_y = -30
                        self.saut = True
                    if touche[pygame.K_KP1] and not self.attaquer:
                        self.attaquer = True
                        self.attaque(surface, cible, 5)  # Coup de poing : 5 dégâts
                        self.der_tmp_combat = pygame.time.get_ticks()
                        self.type_attaque = 1
                    if touche[pygame.K_KP2] and not self.attaquer:
                        self.attaquer = True
                        self.attaque(surface, cible, 10)  # Coup de pied : 10 dégâts
                        self.der_tmp_combat = pygame.time.get_ticks()
                        self.type_attaque = 2

        elif controle == "Manette":
            # Gestion des contrôles manette
            joystick = pygame.joystick.Joystick(self.joueur - 1)  # Récupére le joystick correspondant au joueur
            joystick.init()  # Initialise le module joystick
            axe_x = joystick.get_axis(0)  # Récupére la valeur de l'axe X (gauche/droite) du joystick
            if abs(axe_x) < zone_morte:
                axe_x = 0  # Applique la zone morte
            dirx = axe_x * vitesse  # Calcule la direction horizontale en fonction de l'axe X
            if dirx < 0:
                self.direction = -1  # Changer la direction vers la gauche
            elif dirx > 0:
                self.direction = 1  # Changer la direction vers la droite
            if joystick.get_button(0) and not self.saut:  # bouton X ou A
                self.velo_y = -30
                self.saut = True
            if joystick.get_button(1) and not self.attaquer:  # Bouton O ou B
                self.attaquer = True
                self.attaque(surface, cible, 5)  # Coup de poing : 5 dégâts
                self.der_tmp_combat = pygame.time.get_ticks()
                self.type_attaque = 1
            if joystick.get_button(2) and not self.attaquer:  # Bouton Carré ou X
                self.attaquer = True
                self.attaque(surface, cible, 10)  # Coup de pied : 10 dégâts
                self.der_tmp_combat = pygame.time.get_ticks()
                self.type_attaque = 2
            if joystick.get_button(3) and not self.attaquer:  # bouton Triangle ou Y
                self.attaquer = True
                self.attaque(surface, cible, 20)  # Coup de queue : 20 dégâts
                self.der_tmp_combat = pygame.time.get_ticks()
                self.type_attaque = 3

        self.velo_y += gravite  # Applique la gravité à la vitesse verticale
        diry += self.velo_y  # Calcule la direction verticale

        if self.rect.left + dirx < 0: #si le perso part au négatif
            dirx = -self.rect.left  # Empêche le personnage de sortir de l'écran à gauche
        if self.rect.right + dirx > ecran_long:
            dirx = ecran_long - self.rect.right  # Empêche le personnage de sortir de l'écran à droite
        if self.rect.bottom + diry > ecran_larg - 140:
            self.velo_y = 0  # Arrête la vitesse verticale
            self.saut = False  # Indique que le personnage a atterri
            diry = ecran_larg - 140 - self.rect.bottom  # Empêche le personnage de sortir de l'écran en bas

        # Mise à jour de la position
        self.rect.x += dirx  # Met à jour la position horizontale
        self.rect.y += diry  # Met à jour la position verticale

        if pygame.time.get_ticks() - self.der_tmp_combat > self.attaque_cooldown:#Si l'attaque est TRES récente
            self.attaquer = False  # Réinitialise l'état d'attaque après le cooldown
            self.type_attaque = 0  # Réinitialise le type d'attaque

    def est_mort(self):
        return self.sante <= 0

    def update(self):
        """
        Gère les animations des attaques et du saut

        Paramètres :
        self:numéro du joueur
        """
        if self.attaquer:
            self.rect = pygame.Rect((self.rect.x, self.rect.y, 200, 200))
            if self.type_attaque == 1:
                self.image = self.coup_de_poing
            elif self.type_attaque == 2:
                self.image = self.coup_de_pied
            elif self.type_attaque == 3:
                self.image = self.coup_de_queue
        elif self.saut:
            self.rect = pygame.Rect((self.rect.x, self.rect.y, 140, 200))
            self.image = self.image_saut
        else:
            self.rect = pygame.Rect((self.rect.x, self.rect.y, 140, 200))
            self.image = self.idle_image
        if self.est_mort():
            self.rect = pygame.Rect((self.rect.x, 590, 300, 50))
            self.image = self.image_mort

    def attaque(self, surface, cible, degats):
        """
        Gère la direction des hitbox d'attaques

        Paramètres:
        surface (pygame.Surface) : La surface de l'écran de jeu.
        cible (Combattant) : L'adversaire combattant.
        degats (int) : Les dégâts infligés par l'attaque.
        """
        self.attaquer = True
        if self.direction == -1:
            attaquer_rect = pygame.Rect(self.rect.left - 120, self.rect.y, 120, self.rect.height)  # Zone d'attaque vers la gauche
        else:
            attaquer_rect = pygame.Rect(self.rect.right, self.rect.y, 120, self.rect.height)  # Zone d'attaque vers la droite

        
        if attaquer_rect.colliderect(cible.rect):
            cible.sante -= degats
            print(f"Joueur touché par joueur {self.joueur} (- {degats} HP)")

        if debug:
            # Dessine le rectangle d'attaque en rouge
            pygame.draw.rect(surface, (255, 0, 0), attaquer_rect, 2)

    def des(self, ecran):
        """
        Dessine le combattant sur l'écran

        Paramètres:
        ecran (pygame.Surface) : La surface où sera dessiné le combattant
        """
        # Affiche l'image du combattant
        temp_image = self.image

        # Inverse l'image si le combattant est tourné vers la gauche
        if (self.joueur == 1 and self.direction == -1) or (self.joueur == 2 and self.direction == 1):
            temp_image = pygame.transform.flip(temp_image, True, False)

        if self.est_mort():
            # Pour l'image de mort, redimensionner à une taille réduite
            echelle = 0.55  # (0.7 = 70% de la taille originale) 
            nv_largeur = int(temp_image.get_width() * echelle)
            nv_hauteur = int(temp_image.get_height() * echelle)
            temp_image = pygame.transform.scale(temp_image, (nv_largeur, nv_hauteur))

            # Ajuster la position pour centrer l'image réduite
            decalage_x = (self.rect.width - nv_largeur) // 2
            decalage_y = self.rect.height - nv_hauteur + 20  # 20 pixels de décalage vers le bas

            ecran.blit(temp_image, (self.rect.x + decalage_x, self.rect.y + decalage_y))
        elif self.attaquer or self.saut:
            # Pour les attaques et le saut, conserve la hauteur de l'image idle
            idle_height = self.idle_image.get_height()

            # Calcule le ratio de redimensionnement pour garder la hauteur de l'idle
            scale_height = self.rect.height / idle_height
            nv_largeur = int(temp_image.get_width() * scale_height)

            # Redimensionne l'image
            temp_image = pygame.transform.scale(temp_image, (nv_largeur, self.rect.height))

            # Ajoute un décalage pour les attaques et le saut
            decalage_x = 0
            if self.type_attaque == 1:  # Coup de poing
                if self.direction == 1:  # Punch
                    decalage_x = 15  
                else:
                    decalage_x = -15  # Déplace le coup de poing à gauche de la hitbox
            elif self.type_attaque == 2:  # Coup de pied
                if self.direction == 1:  # Kick
                    decalage_x = 25  
                else:
                    decalage_x = -20  # Déplace le coup de pied à gauche de la hitbox
            elif self.type_attaque == 3:  # Coup de queue
                if self.direction == 1:
                    decalage_x = 25  
                else:
                    decalage_x = -20  # Déplacer le coup de queue à gauche de la hitbox

            ecran.blit(temp_image, (self.rect.x + decalage_x, self.rect.y))
        else:
            # Pour les images idle et autres, redimensionne normalement
            temp_image = pygame.transform.scale(temp_image, (self.rect.width, self.rect.height))
            ecran.blit(temp_image, (self.rect.x, self.rect.y))

        if debug:
            # Dessine le rectangle du combattant en vert
            pygame.draw.rect(ecran, (0, 255, 0), self.rect, 2)

    def afficher_info(self, ecran):
        """
        Affiche les infos du combattant sur l'écran si le débug est activé

        Paramètres:
        ecran (pygame.Surface) : La surface sur laquelle les informations du combattant seront affichées
        """
        pol = pygame.font.SysFont(None, 24)
        info_txt = f"Joueur {self.joueur}: x={self.rect.x}, y={self.rect.y}, HP={self.sante} Attaque={self.type_attaque}, Direction= {self.direction}"
        txt_ecran = pol.render(info_txt, True, (255, 255, 255))
        ecran.blit(txt_ecran, (self.rect.x - 40, self.rect.y - 20))  # Positionne le texte juste au-dessus du personnage