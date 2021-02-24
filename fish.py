import json
import random
import requests

debug = True
deck_size = 52
user_cards = []
app_cards = []
pile_cards = []
cards = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'JACK', 'QUEEN', 'KING', 'ACE']
suits = ['CLUBS','DIAMONDS','HEARTS','SPADES']

def api_request(url):
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)

    return response.text

def shuffle_deck():
    api_response = api_request("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1")
    deck_id = json.loads(api_response)['deck_id']
    print("You are playing with a deck identified as {} and has {} cards total".format(deck_id, deck_size))
    return deck_id

def draw_cards(deck_id):
    api_response = api_request("https://deckofcardsapi.com/api/deck/{}/draw/?count={}".format(deck_id, deck_size))
    pile_cards = json.loads(api_response)["cards"]
    return pile_cards

def pile_check():
    length = len(pile_cards)
    if length:
        if length == 1:
            print ("Only one pile card remaining!")
        else:
            print ("{} cards remaining in the pile".format(length))
        return length
    else:
        print('There are no more cards left to draw and the game is over')

        return score_game()

def user_draw():
    if pile_check():
        drawn_card = pile_cards.pop()
        if drawn_card:
            print('The user has drawn a {} of {}'.format(drawn_card['value'],drawn_card['suit']))
            user_cards.append(drawn_card)
            return drawn_card['value']
    else:
        return False

def app_draw():
    if pile_check():
        drawn_card = pile_cards.pop()
        if drawn_card:
            if debug:
                print('The app has drawn a {} of {}'.format(drawn_card['value'],drawn_card['suit']))
            else:
                print('The app has drawn a card from the pile')
            app_cards.append(drawn_card)
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

def score_game():
    ''' The game is scored by counting which player had the most books, or all four cards of a rank. '''
    user_books = []
    app_books = []
    rank_value = ''

    for rank in cards:
        rank_count = 0
        for user_card in user_cards:
            user_rank = user_card['value']
            if rank == user_rank:
                rank_count += 1
                # print (rank, 'user card')
                if rank_count == 4:
                    print (rank, 'user book')
                    user_books.append(rank)
        rank_count = 0
        for app_card in app_cards:
            app_rank = app_card['value']
            if rank == app_rank:
                rank_count += 1
                # print (rank, 'app card')
                if rank_count == 4:
                    print (rank, 'app book')
                    app_books.append(rank)

    print('User books: ', user_books)
    print('App books: ', app_books)
    if len(app_books) > len(user_books):
        print('The app has won.')
    elif len(app_books) < len(user_books):
        print('The user has won!')
    else:
        print('There appears to be a tie...')
    return False

        #print('{} of {}'.format(card['value'], card['suit'])


def user_guess(auto=True):
    invalid = True
    valid_cards = []
    for card in user_cards:
        if card['value'] not in valid_cards:
            valid_cards.append(card['value'])
    else:
        valid_cards = sorted(tuple(set(valid_cards)))

    if auto:
        return random.choice(valid_cards)

    while invalid:
        prompt = 'Enter the rank of the card from this list: {} '.format(valid_cards)
        guess = input(prompt).upper()
        if guess in valid_cards:
            invalid = False
    return guess.upper()

def app_guess():
    valid_guesses = []
    for card in app_cards:
        if card['value'] not in valid_guesses:
            valid_guesses.append(card['value'])
    return random.choice(valid_guesses)

def check_user_guess():
    guess = user_guess()
    print('The user guesses:', guess)
    caught = 0
    for card in app_cards:
        if card['value'] == guess:
            caught += 1
            user_cards.append(card)
            app_cards.remove(card)
            print("{} of {} card caught by {}".format(card['value'], card['suit'], 'user'))
    else:
        if caught == 0:
            print('The app says, "Go fish!"')
            drawn_card = user_draw()
            if drawn_card == guess:
                print('The user has drawn the guessed rank: {}'.format(drawn_card))
                return True
            else:
                return False
        else:
            if caught == 1:
                print("Nice catch! 1 card caught. Keep guessing...")
            else:
                print("Nice catch! {} cards caught. Keep guessing...".format(caught))
            return True

def check_app_guess():
    guess = app_guess()
    print('The app guesses: {}'.format(guess))
    caught = 0
    for card in user_cards:
        if card['value'] == guess:
            caught += 1
            app_cards.append(card)
            user_cards.remove(card)
            print("{} of {} card caught by {}".format(card['value'], card['suit'], 'app'))
    else:
        if caught == 0:
            print('The user says, "Go fish!"')
            drawn_card = app_draw()
            if drawn_card == guess:
                print('The app has drawn the guessed rank: {}'.format(drawn_card))
                return True
            else:
                return False
        else:
            if caught == 1:
                print("One of the user's cards got caught. The app keeps guessing...")
            else:
                print("The app caught {} cards. The app keeps guessing...".format(caught))
            return True

def random_player():
    players = ('user', 'app')
    return random.choice(players)

def play_game():
    global user_cards, app_cards, pile_cards, player
    playing = True
    deck_id = shuffle_deck()
    pile_cards = draw_cards(deck_id)
    deal_cards()
    show_cards(user_cards, 'user')
    show_cards(app_cards, 'app')
    player = random_player()
    while playing:
        if player == 'user':
            catch = check_user_guess()
            if not catch:
                player = 'app'
        else:
            catch = check_app_guess()
            if not catch:
                player = 'user'
        if not pile_check():
            playing = False


play_game()