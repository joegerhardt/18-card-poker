import pygame
import math

class Display:
    def __init__(self, game):
        self.game = game

        self.background_colour = (100,100,100)
        (self.width, self.height) = (800, 650)
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('18 card poker')
        pygame.font.init()
        
        self.small_font = pygame.font.SysFont('Comic Sans MS', 15)
        self.big_font = pygame.font.SysFont('Comic Sans MS', 40)
        self.name_font = pygame.font.SysFont('Comic Sans MS', 25)

        self.card_offset = 10
        self.card_border = 2
        self.card_size_x, self.card_size_y = 30, 50

        self.table_center_x, self.table_center_y = 400, 300
        self.table_size = 250

        self.button_radius = 190

    def update(self):

        players = self.game.players

        self.screen.fill(self.background_colour)
        pygame.draw.circle(self.screen, (150,150,0), (400,300), 260)
        pygame.draw.circle(self.screen, (0,255,0), (400,300), 250)

        pot = self.big_font.render('Pot: $' + str(self.game.pot), True, (0,0,0))
        self.screen.blit(pot, (self.table_center_x-pot.get_width()//2, self.table_center_y-pot.get_height()//2+50))

        for index, player in enumerate(players):
            radians = index * 2 * math.pi / len(players) + math.pi / 2
            player_x = self.table_center_x+self.table_size*math.cos(radians)
            player_y = self.table_center_y+self.table_size*math.sin(radians)

            if player.hand != () and player.name == 'alice':
                
                pygame.draw.rect(self.screen, (0,0,0), (player_x-37, player_y-27, 34, 54))
                pygame.draw.rect(self.screen, (0,0,0), (403+250*math.cos(radians), 273+250*math.sin(radians), 34, 54))
                pygame.draw.rect(self.screen, (255,255,255), (365+250*math.cos(radians), 275+250*math.sin(radians), 30, 50))
                pygame.draw.rect(self.screen, (255,255,255), (405+250*math.cos(radians), 275+250*math.sin(radians), 30, 50))

                num = self.big_font.render(str(player.hand[0]), True, (0,0,0))
                self.screen.blit(num, (367+250*math.cos(radians), 270+250*math.sin(radians)))
                num = self.big_font.render(str(player.hand[1]), True, (0,0,0))
                self.screen.blit(num, (407+250*math.cos(radians), 270+250*math.sin(radians)))
            if player == self.game.current_player:
                name = self.name_font.render(str(player.name).capitalize() + ': $' + str(player.stack), True, (255,255,0)) 
            else:
                name = self.name_font.render(str(player.name).capitalize() + ': $' + str(player.stack), True, (0,0,0))        
            if player_y > self.table_center_y:
                #display player name underneath
                self.screen.blit(name, (player_x-name.get_width()//2, player_y-name.get_height()//2+50))
            else:
                self.screen.blit(name, (player_x-name.get_width()//2, player_y-name.get_height()//2-50))


            if self.game.dealer == player:
                pygame.draw.circle(self.screen, (255,255,255), (400+self.button_radius*math.cos(radians), 300+self.button_radius*math.sin(radians)), 10)
                dealer = self.small_font.render("D", True, (0,0,0))
                self.screen.blit(dealer, (395+self.button_radius*math.cos(radians), 290+self.button_radius*math.sin(radians)))
            elif self.game.small_blind_player == player:
                pygame.draw.circle(self.screen, (255,0,0), (400+self.button_radius*math.cos(radians), 300+self.button_radius*math.sin(radians)), 10)
                dealer = self.small_font.render("SB", True, (0,0,0))
                self.screen.blit(dealer, (390+self.button_radius*math.cos(radians), 290+self.button_radius*math.sin(radians)))
            elif self.game.big_blind_player == player:
                pygame.draw.circle(self.screen, (0,0,255), (400+self.button_radius*math.cos(radians), 300+self.button_radius*math.sin(radians)), 10)
                dealer = self.small_font.render("BB", True, (0,0,0))
                self.screen.blit(dealer, (390+self.button_radius*math.cos(radians), 290+self.button_radius*math.sin(radians)))

            
            if self.game.total_bets[player] > 0:
                bet = self.small_font.render(str(self.game.total_bets[player]), True, (0,0,0))
                self.screen.blit(bet, (self.table_center_x+160*math.cos(radians)-bet.get_width()//2,
                                       self.table_center_y+160*math.sin(radians)-bet.get_height()//2))
         




        total_public_cards = sum(self.game.betting_stage_public_cards)
        for i in range(total_public_cards):
            pygame.draw.rect(self.screen, (0,0,0), (int(self.table_center_x-self.card_border+(self.card_size_x+self.card_offset)*(i-total_public_cards/2)),
                                               self.table_center_y-self.card_border-self.card_size_y//2-self.card_border, 34, 54))
            if i < len(self.game.table_cards):
                pygame.draw.rect(self.screen, (255,255,255), (int(self.table_center_x+(self.card_size_x+self.card_offset)*(i-total_public_cards/2)),
                                                         self.table_center_y-self.card_size_y//2-self.card_border, 30, 50))
                num = self.big_font.render(str(self.game.table_cards[i]), True, (0,0,0))
                self.screen.blit(num, (int(self.table_center_x+2+(self.card_size_x+self.card_offset)*(i-total_public_cards/2)),
                                  self.table_center_y-5-self.card_size_y//2-self.card_border))
            else:
                pygame.draw.rect(self.screen, (255,0,0), (int(self.table_center_x+(self.card_size_x+self.card_offset)*(i-total_public_cards/2)),
                                                     self.table_center_y-self.card_size_y//2-self.card_border, 30, 50))
                
        
        for i, player in enumerate(players):
            score = self.small_font.render(player.name+": "+str(round(self.game.scores[player]/max(self.game.num_hands, 1)/self.game.big_blind_amount, 3))+"BB", True, (0,0,0))
            self.screen.blit(score, (10,10+30*i))
                
        pygame.display.flip()
            

        