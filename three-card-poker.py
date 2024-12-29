import random

# Create a deck of cards
suits = ['♠', '♥', '♦', '♣']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
deck = [f'{rank}{suit}' for suit in suits for rank in ranks]
bankroll = 100
wager = 0
dealer_hand = ''
player_hand = ''

# Define the hand rankings
hand_rankings = {
    'Royal Flush': 10,
    'Straight Flush': 9,
    'Four of a Kind': 8,
    'Full House': 7,
    'Flush': 6,
    'Straight': 5,
    'Three of a Kind': 4,
    'Two Pair': 3,
    'One Pair': 2,
    'High Card': 1
}

def evaluate_hand(hand):
    # Convert face cards to numbers and separate suits
    card_map = {'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    values = []
    suits = []
    
    for card in hand:
        value = card[:-1]  # Modified to handle '10' correctly
        suit = card[-1]
        
        if value in card_map:
            value = card_map[value]
        else:
            value = int(value)
            
        values.append(value)
        suits.append(suit)
    
    # Sort values in descending order for easier comparison
    values.sort(reverse=True)
    
    # Check for flush
    is_flush = len(set(suits)) == 1
    
    # Check for straight
    is_straight = False
    if values == [14, 2, 3]:  # Special case: Ace-2-3
        is_straight = True
        values = [3, 2, 1]  # Ace is low in this case
    else:
        is_straight = (values[0] - values[2] == 2) and (len(set(values)) == 3)
    
    # Check for straight flush and royal flush
    if is_straight and is_flush:
        if values == [14, 13, 12]:
            return (hand_rankings['Royal Flush'], values)
        return (hand_rankings['Straight Flush'], values)
    
    # Count frequencies of values
    value_counts = {}
    for value in values:
        value_counts[value] = value_counts.get(value, 0) + 1
    
    # Check for three of a kind
    if 3 in value_counts.values():
        return (hand_rankings['Three of a Kind'], values)
    
    # Check for pair
    if 2 in value_counts.values():
        paired_value = [v for v, count in value_counts.items() if count == 2][0]
        kicker = [v for v in values if v != paired_value][0]
        return (hand_rankings['One Pair'], [paired_value, kicker])
    
    # Check for flush
    if is_flush:
        return (hand_rankings['Flush'], values)
    
    # Check for straight
    if is_straight:
        return (hand_rankings['Straight'], values)
    
    # High card
    return (hand_rankings['High Card'], values)

def compare_hands(player_hand, dealer_hand):
    player_result = evaluate_hand(player_hand)
    dealer_result = evaluate_hand(dealer_hand)
    
    # Compare hand ranks
    if player_result[0] > dealer_result[0]:
        return 1
    elif player_result[0] < dealer_result[0]:
        return -1
    
    # If ranks are equal, compare values
    for p_val, d_val in zip(player_result[1], dealer_result[1]):
        if p_val > d_val:
            return 1
        elif p_val < d_val:
            return -1
    
    # If all values are equal, it's a tie
    return 0

def dealer_qualifies(hand):
    result = evaluate_hand(hand)
    if result[0] > hand_rankings['High Card']:  # Any pair or better automatically qualifies
        return True
    
    # For high card hands, check if highest card is at least Queen (12)
    values = result[1]
    return values[0] >= 12  # 12 represents Queen

def determine_winner():
    global bankroll, wager
    result = compare_hands(player_hand, dealer_hand)
    
    # Get hand names for display
    player_hand_name = [name for name, rank in hand_rankings.items() 
    if rank == evaluate_hand(player_hand)[0]][0]
    dealer_hand_name = [name for name, rank in hand_rankings.items() 
    if rank == evaluate_hand(dealer_hand)[0]][0]
    
    print(f"\nYour hand: {player_hand_name}")
    print(f"Dealer's hand: {dealer_hand_name}")
    
    # Check dealer qualification
    if not dealer_qualifies(dealer_hand):
        print("Dealer does not qualify (less than Queen high)")
        print("Player automatically wins play bet!")
        bankroll += wager  # Return ante (first bet)
        bankroll += (wager * 2)  # Win on play bet
    else:
        print("Dealer qualifies")
        if result == 1:
            print("Player wins!")
            bankroll += (wager * 4)  # Win both bets (1 ante + 2 play)
        elif result == -1:
            print("Dealer wins!")
        else:
            print("It's a tie!")

def deal_player():
    global bankroll, wager, player_hand, deck
    print(f"\nYou have ${bankroll} available")
    wager_input = input("How much would you like to bet? ").strip()
    try:
        wager = float(wager_input)
        if wager <= 0 or wager > bankroll:
            print("Wager must be greater than zero and less than or equal to your bankroll.")
            return False 
        else:
            print(f"You have wagered ${wager}")
            
            # Deal three random cards and remove them from the deck
            dealt_cards = random.sample(deck, 3)
            print("You have been dealt: " + ", ".join(dealt_cards))
            player_hand = dealt_cards
            
            # Remove the dealt cards from the deck
            for card in dealt_cards:
                deck.remove(card)
            
            # Update the bankroll after the wager
            bankroll -= wager 
            return True

    except ValueError:
        print("Invalid input. Please enter a valid number for your wager.")
        return False

def deal_house():
    global dealer_hand, deck
    house_cards = random.sample(deck, 3)
    dealer_hand = house_cards
    print("Dealer gets: " + " ".join(house_cards))

def player_decision():
    global bankroll, wager
    print(f"\nYou have ${bankroll} and the bet is ${wager}, do you wish to play?")
    decision = input("Enter 'Y' to match your bet or 'N' to fold: ").strip().upper()
    
    if decision == 'N':
        print("You fold.")
        return False
    
    elif decision == 'Y':
        print(f"You call for ${wager} more.")
        bankroll -= wager
        return True
    
    else:
        print("Invalid input. Please enter 'Y' or 'N'.")
        return player_decision()

def reset_deck():
    """Reset the deck to its original state"""
    global deck
    deck = [f'{rank}{suit}' for suit in suits for rank in ranks]

# Start the program loop
while True:
    reset_deck()  # Reset deck at the start of each hand
    
    if not deal_player():  # While dealing player cards
        continue  # Restart if there was an issue with wagering
    
    if not player_decision():  # Check player's decision
        continue  # If player folded, start a new hand
    
    # Proceed to deal house only if player did not fold
    deal_house()
    
    # Determine and announce winner
    determine_winner()
    
    print(f"\nYour current bankroll: ${bankroll}")
    
    # Ask if they want to play another hand or exit
    again = input("Do you want to play another hand? (Y/N): ").strip().upper()
    if again != 'Y':
        print(f"\nThank you for playing! You're leaving with ${bankroll}!")
        break