#!/usr/bin/python
''' A simple implementation of Go Fish

The rules are modified from the standard Go Fish rules:

Rule 1: Two player game with user versus computer.
    players = ('user', 'app')

Rule 2: Each player is dealt seven cards from a 52 card deck at game start.
    deal_cards()

Rule 3: The cards not dealt to the players are put into the pile.
    pile_cards

Rule 4: Randomly either the user or the computer has the first turn.
    random_player()

Rule 5: A guess must be from a the rank of 2s up to Aces and only for the ranks
held that player.
    ranks[]
    app_cards[]
    user_cards[]
    app_guess()
    user_guess()

Rule 6: Guesses must be a number or the name of the rank. Guesses for the app
are always automatic, and automated boolean determines if user guesses are
    ranks[]
    app_guess()
    user_guess()

Rule 7: If a guess is correct, then the player get another turn to guess.
    check_app_guess()
    check_user_guess()
    game_loop()

Rule 8: If a guess results in player having four suits of a rank, then a book is scored.
    score_app()
    score_user()

Rule 9: If a guess is wrong, the player must draw a card from the pile and lose their turn.
    app_draw()
    user_draw()
    check_app_guess()
    check_user_guess()

Rule 10: If the player draws the card guessed, their turn contines, otherwise,
the it's the other player turn to guess.
    check_app_guess()
    check_user_guess()

Rule 11: When all thirteen books have been scored with all suits of a rank,
or a player has no more cards, or the pile is empty the game is over.
    check_app_guess()
    check_user_guess()
    check_pile()

Rule 12: When the game is over, the player with the most books scored wins.
    score_app()
    score_user()
    score_game()

Rule 13: The API for creating a shuffled deck and drawing cards is from deckofcardsapi.com.
Thank you for the inspiration to create this game!
    api_request()
    shuffle_deck()
    draw_cards()

'''
# necessary modules
import json
import random
import requests

# global variables
automated = True    # if True the game is automated for user guesses
debug = False       # if True print additional troubleshooting information
deck_id = ''        # to draw cards after initial shuffle
deck_size = 52      # size of one deck of cards
app_cards = []      # list of cards held by the app
user_cards = []     # list of cards held by the user
app_books = []      # list of ranks that app had all four suits
user_books = []     # list of ranks that user had all four suits
pile_cards = []     # the pile of cards that the app and user draw from on a wrong guess
players = ('user', 'app') # Names of players for the game output and turns
playing = True      # flag when to stop the game_loop function
ranks = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'JACK', 'QUEEN', 'KING', 'ACE')
suits = ('CLUBS','DIAMONDS','HEARTS','SPADES') # reserver for future use

def api_request(url):
    ''' Execute an GET request to url parameter with no headers or data sent and return response.text '''
    response = requests.request("GET", url, headers={}, data={})
    return response.text

def shuffle_deck():
    global deck_id
    ''' Execute an API request to get a new deck of cards and return the deck_id '''
    api_response = api_request("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1")
    deck_id = json.loads(api_response)['deck_id']
    if debug:
        print("Deck {} has a total of {} cards.".format(deck_id, deck_size))
    return deck_id

def draw_cards(deck_id):
    ''' Execute an API request to draw all cards in the deck to return as the pile of cards to deal '''
    api_response = api_request("https://deckofcardsapi.com/api/deck/{}/draw/?count={}".format(deck_id, deck_size))
    pile_cards = json.loads(api_response)["cards"]
    return pile_cards

def pile_check():
    ''' Check the pile of cards to see if there are any left to draw and return boolean '''
    global playing
    length = len(pile_cards) # length is how many cards remaining
    if length:
        if length == 1:
            print ("Only one pile card remaining!")
        else:
            print ("{} cards remaining in the pile".format(length))
        return length
    else:
        playing = False
        print('Next player\'s turn, there are no more cards left to draw.')
        return False

def app_draw():
    global players
    if pile_check():
        drawn_card = pile_cards.pop()
        if drawn_card:
            if debug:
                print('The {} has drawn a {} of {}.'.format(
                    players[1], drawn_card['value'], drawn_card['suit']))
            else:
                print('The {} has drawn a card from the pile.'.format(players[1]))
            app_cards.append(drawn_card)
            return drawn_card['value']
    else:
        return False

def user_draw():
    ''' The user gets one card appended to the user_cards list and removed from the pile_cards list '''
    if pile_check():
        drawn_card = pile_cards.pop()
        if drawn_card:
            print('The {} has drawn a {} of {}'.format(
                    players[0], drawn_card['value'], drawn_card['suit']))
            user_cards.append(drawn_card)
            return drawn_card['value']
    else:
        return False

def deal_cards():
    draw_count = 7
    for card in range(draw_count * 2):
        if card % 2:
            user_draw()
        else:
            app_draw()

def show_cards(cards, player):
    length = len(cards)
    print ("The {} has {} cards:\n".format(player, length))
    print(len(pile_cards),"pile cards left.")
    sorted_cards = []
    for card in cards:
        sorted_cards.append("{}\t of {}".format(card["value"], card["suit"]))
    sorted_cards.sort()
    for card in sorted_cards:
        print(card)

def score_app():
    for rank in ranks:
        rank_count = 0
        for app_card in app_cards:
            if rank == app_card['value']:
                rank_count += 1
                if rank_count == 4:
                    print ('The app has scored the book for rank {}.'.format(rank))
                    app_books.append(rank)
        for rank in app_books:
            for card in app_cards[:]:
                if card['value'] == rank:
                    app_cards.remove(card)
    if debug:
        print('App books:', app_books)

def score_user():
    for rank in ranks:
        rank_count = 0
        for user_card in tuple(user_cards):
            if rank == user_card['value']:
                rank_count += 1
                if rank_count == 4:
                    print ('The user has scored the book for rank {}.'.format(rank))
                    user_books.append(rank)
        for rank in user_books:
            for card in user_cards:
                if card['value'] == rank:
                    user_cards.remove(card)
    if debug:
        print('User books:', user_books)

def score_game():
    ''' The game is scored by counting which player had the most books, or all four cards of a rank. '''
    score_app()
    score_user()
    print('User books: ', user_books)
    if debug: print('User cards: ', user_cards)
    print('App books: ', app_books)
    if debug: print('App cards: ', app_cards)
    if len(app_books) > len(user_books):
        print('The app has won.')
    elif len(app_books) < len(user_books):
        print('The user has won!')
    else:
        print('There appears to be a tie...')
    return False

def app_guess():
    valid_guesses = []
    for card in app_cards:
        if card['value'] not in valid_guesses:
            valid_guesses.append(card['value'])
    if valid_guesses:
        return random.choice(valid_guesses)
    else:
        return False

def check_app_guess():
    global playing
    guess = app_guess()
    if not guess: # app has no more cards to make a valid guess
        playing = False
        return False
    else:
        print('The app guesses: {}'.format(guess))
    caught = 0
    for card in user_cards:
        if card['value'] == guess:
            caught += 1
            app_cards.append(card)
            user_cards.remove(card)
            print("{} of {} card caught by {}".format(card['value'], card['suit'], 'app'))
    else: # else clause executes when for loop has finished
        if caught == 0:
            print('The user says, "Go fish!"')
            drawn_card = app_draw()
            if drawn_card == guess:
                print('The app has drawn the guessed rank: {}'.format(drawn_card))
                score_app()
                return True
            else:
                return False
        else:
            score_app()
            if caught == 1:
                print("One of the user's cards got caught. The app keeps guessing...")
            else:
                print("The app caught {} cards. The app keeps guessing...".format(caught))
            return True

def user_guess():
    invalid = True
    valid_cards = []
    for card in user_cards:
        if card['value'] not in valid_cards:
            valid_cards.append(card['value'])
    else:
        valid_cards = sorted(tuple(set(valid_cards)))
    if not valid_cards:
        return False
    if automated and valid_cards:
        return random.choice(valid_cards)
    else:
        show_cards(user_cards, players[0])

    while invalid:
        prompt = 'Enter the rank of the card from this list: {} '.format(valid_cards)
        guess = input(prompt).upper()
        if guess in valid_cards:
            invalid = False
    return guess.upper()

def check_user_guess():
    global playing
    guess = user_guess()
    if not guess:
        playing = False # user has no more cards to make a valid guess
        return False
    else:
        print('The user guesses:', guess)
    caught = 0
    for card in app_cards:
        if card['value'] == guess:
            caught += 1
            user_cards.append(card)
            app_cards.remove(card)
            print("{} of {} card caught by {}".format(card['value'], card['suit'], 'user'))
    else: # else clause executes when for loop has finished
        if caught == 0:
            print('The app says, "Go fish!"')
            drawn_card = user_draw()
            if drawn_card == guess:
                print('The user has drawn the guessed rank: {}'.format(drawn_card))
                score_user()
                return True
            else:
                return False
        else:
            score_user()
            if caught == 1:
                print("Nice catch! 1 card caught. Keep guessing...")
            else:
                print("Nice catch! {} cards caught. Keep guessing...".format(caught))
            return True

def random_player():
    return random.choice(players)

def game_loop():
    global player
    player = random_player()
    while playing:
        show_cards(user_cards, players[0])
        if player == players[0]:
            catch = check_user_guess()
            if not catch:
                player = players[1]
        else:
            catch = check_app_guess()
            if not catch:
                player = players[0]
    score_game()

def play_game():
    global app_cards, app_books, user_cards, user_books
    global deck_id, pile_cards, playing
    deck_id = shuffle_deck()
    pile_cards = draw_cards(deck_id)
    app_cards.clear()
    user_cards.clear()
    app_books.clear()
    user_books.clear()
    deal_cards()
    if debug: show_cards(user_cards, 'user')
    if debug: show_cards(app_cards, 'app')
    playing = True
    game_loop()

if __name__=='__main__':

    while 1:
        answer = input('Do you want to play "Go Fish"? (y/n)').lower()
        if answer and answer[0]== 'y':
            play_game()
        else:
            break