import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

import mouse

import chess
import chess.engine
import chess.pgn

#from stockfish import Stockfish

import random

game = chess.Board()

#engine = Stockfish(path="stockfish-windows-2022-x86-64-avx2.exe", depth=18, parameters={ "Threads": 7, "Hash": 2048 })

#engine.set_elo_rating(1800)

#engine.set_skill_level(20)

engine = chess.engine.SimpleEngine.popen_uci("stockfish-windows-x86-64-avx2.exe")

#engine.configure({"Hash": 1024, "Threads": 7, "UCI_Elo": 1350, "UCI_LimitStrength": True, "Slow Mover": 750})

engine.configure({"UCI_LimitStrength": True, "UCI_Elo": 1500, "Threads": 2, "Hash": 32})
#engine.configure({"Skill Level": 12})

#engine.configure({"Skill Level": 20, "Threads": 2, "Hash": 32})

driver = webdriver.Chrome()

driver.maximize_window()
#driver.fullscreen_window()
driver.get("https://www.chess.com/play/online/")

time.sleep(1)

'''
pieces = board.find_elements(By.XPATH, "./*")



for i in pieces:
    if i.get_attribute("class") == "piece wp square-52":
        i.click()
'''



move_count = 0

white_move_to_play = "-"
black_move_to_play = "-"

move_speed = 0

endings = ["1-0", "0-1", "1/2-1/2"]

game_is_over = False

#print()

username = "DeggyFive"

input()

#print("".join(driver.find_element(By.CLASS_NAME, "player-tagline").text[0:13]))
#is_white = "".join(driver.find_element(By.CLASS_NAME, "player-tagline").text[0:len(username)]) != username

is_white = "flipped" not in driver.find_element(By.ID, "board-single").get_attribute("class")

if is_white:
    print("Playing as White")
else:
    print("Playing as Black")

board_size_8ths = driver.find_element(By.ID, "board-single").rect['width'] / 8


while True:
    try:
            driver.find_element(By.CLASS_NAME, "new-game-buttons-component").find_elements(By.TAG_NAME, "button")[0].click()
    except:
        pass
    else:
        game_is_over = True
        time.sleep(5)

    if game_is_over:
        game = chess.Board()
        #print("".join(driver.find_element(By.CLASS_NAME, "player-tagline").text[0:10]))
        
        move_count = 0
        white_move_to_play = "-"
        black_move_to_play = "-"
        game_is_over = False

        is_white = "flipped" not in driver.find_element(By.ID, "board-single").get_attribute("class")

        if is_white:
            print("Playing as White")
        else:
            print("Playing as Black")

    new_move = False

    #print(f"{game}\n")
    #time.sleep(0.5)

    #print(mouse.get_position())

    try:
        if not is_white:
            recent_white_move = driver.find_elements(By.TAG_NAME, "vertical-move-list").pop().find_elements(By.XPATH, "./*").pop().find_elements(By.XPATH, "./*")[0].text

            if recent_white_move != white_move_to_play:
                white_move_to_play = recent_white_move
                new_move = True
        else:
            recent_black_move = driver.find_elements(By.TAG_NAME, "vertical-move-list").pop().find_elements(By.XPATH, "./*").pop().find_elements(By.XPATH, "./*")[2].text

            if recent_black_move != black_move_to_play:
                black_move_to_play = recent_black_move
                new_move = True

        #print(recent_white_move)
        #print(recent_black_move)
    except:
        pass
    finally:

        if endings.__contains__(white_move_to_play) or endings.__contains__(black_move_to_play):
            game_is_over = True
            continue
        
        try:
            black_time_segments = driver.find_elements(By.CLASS_NAME, "clock-time-monospace")[0].text.replace('.', ':').split(':')
            white_time_segments = driver.find_elements(By.CLASS_NAME, "clock-time-monospace")[1].text.replace('.', ':').split(':')
        except:
            game_is_over = True
            continue

        black_time = int(black_time_segments[0]) * 60 + int(black_time_segments[1])
        if len(black_time_segments) == 3:
            black_time += int(black_time_segments[2]) * 0.1

        white_time = int(white_time_segments[0]) * 60 + int(white_time_segments[1])
        if len(white_time_segments) == 3:
            white_time += int(white_time_segments[2]) * 0.1

        try:
            driver.find_element(By.CLASS_NAME, "draw-offer-component").find_element(By.TAG_NAME, "a").click()
        except:
            pass
        
        #print(f"White Time: {':'.join(white_time_segments)}")
        #print(f"Black Time: {':'.join(black_time_segments)}")

        if is_white:
            if move_count == 0:
                move = engine.play(game, chess.engine.Limit(time=2.2), ponder=True).move.uci()

                print(move)

                move_start_file = ord(move[0]) - 96
                move_start_rank = int(move[1])

                move_end_file = ord(move[2]) - 96
                move_end_rank = int(move[3])

                game.push_uci(move)

                #print(move)

                move_is_promotion = len(move) == 5

                promotion_click_y_offset = 0

                board_size_8ths = driver.find_element(By.ID, "board-single").rect['width'] / 8

                if move_is_promotion:
                    piece_promote = move[4]

                    if piece_promote == "q":
                        promotion_click_y_offset = 0
                    elif piece_promote == "n":
                        promotion_click_y_offset = board_size_8ths
                    elif piece_promote == "r":
                        promotion_click_y_offset = board_size_8ths * 2
                    elif piece_promote == "b":
                        promotion_click_y_offset = board_size_8ths * 3
                    

                piece_element = driver.find_element(By.CLASS_NAME, f"square-{move_start_file}{move_start_rank}")
                start_location = piece_element.location
                x_offset = -board_size_8ths * (move_start_file - move_end_file)
                y_offset = board_size_8ths * (move_start_rank - move_end_rank)
                ActionChains(driver, duration=0)\
                    .click(piece_element)\
                    .move_to_element_with_offset(piece_element, x_offset, y_offset)\
                    .click()\
                    .perform()
                
                if move_is_promotion:
                    ActionChains(driver, duration=0)\
                    .move_by_offset(0, promotion_click_y_offset)\
                    .click()\
                    .perform()

                move_count += 1
            elif new_move:
                game.push_san(black_move_to_play)

                move = engine.play(game, chess.engine.Limit(white_clock=white_time, black_clock=black_time), ponder=True).move.uci()

                print(f"White Move: {move}")

                move_start_file = ord(move[0]) - 96
                move_start_rank = int(move[1])

                move_end_file = ord(move[2]) - 96
                move_end_rank = int(move[3])

                game.push_uci(move)

                #print(move)

                move_is_promotion = len(move) == 5

                promotion_click_y_offset = 0

                board_size_8ths = driver.find_element(By.ID, "board-single").rect['width'] / 8

                if move_is_promotion:
                    piece_promote = move[4]

                    if piece_promote == "q":
                        promotion_click_y_offset = 0
                    elif piece_promote == "n":
                        promotion_click_y_offset = board_size_8ths
                    elif piece_promote == "r":
                        promotion_click_y_offset = board_size_8ths * 2
                    elif piece_promote == "b":
                        promotion_click_y_offset = board_size_8ths * 3
                    

                piece_element = driver.find_element(By.CLASS_NAME, f"square-{move_start_file}{move_start_rank}")
                start_location = piece_element.location
                x_offset = -board_size_8ths * (move_start_file - move_end_file)
                y_offset = board_size_8ths * (move_start_rank - move_end_rank)
                ActionChains(driver, duration=0)\
                    .click(piece_element)\
                    .move_to_element_with_offset(piece_element, x_offset, y_offset)\
                    .click()\
                    .perform()
                
                if move_is_promotion:
                    ActionChains(driver, duration=0)\
                    .move_by_offset(0, promotion_click_y_offset)\
                    .click()\
                    .perform()

                move_count += 1
        else:
            if new_move:
                game.push_san(white_move_to_play)

                if move_count == 0:
                    move = engine.play(game, chess.engine.Limit(time=2.2), ponder=True).move.uci()
                else:
                    move = engine.play(game, chess.engine.Limit(white_clock=white_time, black_clock=black_time), ponder=True).move.uci()

                move_start_file = ord(move[0]) - 96
                move_start_rank = int(move[1])

                move_end_file = ord(move[2]) - 96
                move_end_rank = int(move[3])

                game.push_uci(move)

                print(f"Black Move: {move}")

                move_is_promotion = len(move) == 5

                promotion_click_y_offset = 0

                board_size_8ths = driver.find_element(By.ID, "board-single").rect['width'] / 8
                
                if move_is_promotion:
                    piece_promote = move[4]

                    if piece_promote == "q":
                        promotion_click_y_offset = 0
                    elif piece_promote == "n":
                        promotion_click_y_offset = -board_size_8ths
                    elif piece_promote == "r":
                        promotion_click_y_offset = -board_size_8ths * 2
                    elif piece_promote == "b":
                        promotion_click_y_offset = -board_size_8ths * 3

                '''
                mouse.move(335 + 100 * (8 - move_start_file), 925 - 100 * (8 - move_start_rank), duration=move_speed)
                mouse.click()

                mouse.move(335 + 100 * (8 - move_end_file), 925 - 100 * (8 - move_end_rank), duration=move_speed)
                mouse.click()

                if move_is_promotion:
                    mouse.move(335 + 100 * (8 - move_end_file), 925 - 100 * (8 - move_end_rank) + promotion_click_y_offset, duration=move_speed)
                    mouse.click()
                '''

                piece_element = driver.find_element(By.CLASS_NAME, f"square-{move_start_file}{move_start_rank}")
                start_location = piece_element.location
                x_offset = board_size_8ths * (move_start_file - move_end_file)
                y_offset = -board_size_8ths * (move_start_rank - move_end_rank)
                ActionChains(driver, duration=0)\
                    .click(piece_element)\
                    .move_to_element_with_offset(piece_element, x_offset, y_offset)\
                    .click()\
                    .perform()
                
                if move_is_promotion:
                    ActionChains(driver, duration=0)\
                    .move_by_offset(0, promotion_click_y_offset)\
                    .click()\
                    .perform()

                move_count += 1
    


while False:
    time.sleep(3)
    move = engine.play(game, chess.engine.Limit(time=2)).move.uci()
    game.push_uci(move)

    move_start_file = ord(move[0]) - 96
    move_start_rank = int(move[1])

    move_end_file = ord(move[2]) - 96
    move_end_rank = int(move[3])

    mouse.move(386 + 96 * move_start_file, 972 - 96 * move_start_rank, duration=0.1)
    mouse.click()

    mouse.move(386 + 96 * move_end_file, 972 - 96 * move_end_rank, duration=0.1)
    mouse.click()
    
