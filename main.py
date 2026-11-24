from drafter import *
from dataclasses import dataclass

set_website_title("DocuChess")
set_site_information(
    author="Patrick McLaughlin",
    description="Record chess games for for documentation.",
    sources="Thanks to the Drafter Documentation site.",
    planning="",
    links=["https://github.com/pat-mclaughlin/chess-game-documentation"]
)
hide_debug_information()
set_website_framed(False)

@dataclass 
class Game:
    opponent: str
    moves: list[str]
    is_white: bool
    results: str
    result_factor: str
    date: str

@dataclass
class State:
    library: list[Game]
    current_game: Game
    search_term: str
    search_type: str
    sort_option: str

def list_moves(list: list[str]) -> str:
    if not list:
        return "No Moves Recorded"
    updated_list = []
    for move_index, move in enumerate(list):
        split_move = move.split("|")
        first_move = split_move[0]
        second_move = split_move[1]
        updated_list.append(str(move_index+1) +". " + first_move + " " + second_move)
    move_string = "\n".join(updated_list).strip()
    return move_string
        
def date_to_int(date: str) -> int:
    new_date = date.replace("-","")
    return int(new_date)

def count_moves(game: Game) -> int:
    count = 0
    for turn in game.moves:
        count += 1
    return count

def sort_games(key: str, list: list[Game]) -> list[Game]:
    change_made = True
    sorted_list = []
    for game in list:
        sorted_list.append(game)
    if key == "Opponent":
        while change_made:
            change_made = False
            for game_index in range(0,len(list)-1):
                if sorted_list[game_index].opponent > sorted_list[game_index+1].opponent:
                    temp = sorted_list[game_index]
                    sorted_list[game_index] = sorted_list[game_index+1]
                    sorted_list[game_index+1] = temp
                    change_made = True
    if key == "Earliest":
        while change_made:
            change_made = False
            for game_index in range(0,len(list)-1):
                if date_to_int(sorted_list[game_index].date) > date_to_int(sorted_list[game_index+1].date):
                    temp = sorted_list[game_index]
                    sorted_list[game_index] = sorted_list[game_index+1]
                    sorted_list[game_index+1] = temp
                    change_made = True
    if key == "Latest":
        while change_made:
            change_made = False
            for game_index in range(0,len(list)-1):
                if date_to_int(sorted_list[game_index].date) < date_to_int(sorted_list[game_index+1].date):
                    temp = sorted_list[game_index]
                    sorted_list[game_index] = sorted_list[game_index+1]
                    sorted_list[game_index+1] = temp
                    change_made = True
    if key == "Num. of Moves":
        while change_made:
            change_made = False
            for game_index in range(0,len(list)-1):
                if count_moves(sorted_list[game_index]) < count_moves(sorted_list[game_index+1]):
                    temp = sorted_list[game_index]
                    sorted_list[game_index] = sorted_list[game_index+1]
                    sorted_list[game_index+1] = temp
                    change_made = True  
    return sorted_list

def filter_games(term: str, type: str, list: list[Game]) -> list[Game]:
    filtered_list = []
    if not term.strip():
        return list
    if type == "Opponent":
        for game in list:
            if term.strip() == game.opponent:
                filtered_list.append(game)
    if type == "General Outcome":
        for game in list:
            if term.strip() == game.results:
                filtered_list.append(game)
    if type == "Date":
        for game in list:
            if term.strip() == game.date:
                filtered_list.append(game)
    return filtered_list

def legal_notation(move: str)-> bool:
    if not move:
        return False
    if move == "...":
        move = ""
        return True
    if move == "O-O" or move == "O-O-O" or move == "O-O+" or move == "O-O-O+" or move == "O-O#" or move == "O-O-O#":
        return True
    for char in move:
        if char not in "abcdefgh12345678KQRBNKQRBNx+#=":
            return False
    for i, char in enumerate(move):
        if char in "#+":
            if i != len(move) -1:
                return False
        if char in "12345678":
            if i == 0:
                return False
            if move[i-1] not in "abcdefghKQRBN":
                return False
        if char == "=":
            if i == len(move) - 1:
                return False
            if move[i+1] not in "QRBN":
                return False
    return True
def result_stats(games: list[Game])-> list[int]:
    if not games:
        return [0,0,0,0]
    wins = 0
    losses = 0
    draws = 0
    incompletes = 0
    for game in games:
        result = game.results
        if result == "Win":
            wins +=1
        elif result == "Loss":
            losses += 1
        elif result == "Draw":
            draws += 1
        else:
            incompletes += 1
    return [wins,losses,draws,incompletes]
    
add_description = ("Add moves to your games according to Algebraic Notation.\n"
                  "If you unsure of how the record a move, visit this website:\n"
                  "https://www.chess.com/terms/chess-notation\n"
                   "If you only need to record the first move, type '...' in the second move to add it.")
                
    
    
@route
def index(state: State) -> Page:
    return Page(state, [
        "Home\n", 
        Button("Library", "game_library"),
        Button("New Game", "new_game")
    ])
@route
def back(state: State, page: str) -> Page:
    if page == "home":
        return index(state)
    else:
        return game_library(state) 
    

@route
def new_game(state: State) -> Page:
    return Page(state, [
        "New Game\n",
        "Opponent's name:", TextBox("name"), Button("Back", "back", Argument("page","home")), "\n",
        "Date:", DateInput("date","1111-11-11"), "\n",
        "Piece Color:", RadioButtonGroup("color",["White","Black"],"White"), Button("Next","update_prerequisite")
    ])

@route
def update_prerequisite(state: State, name: str, date: str, color: str) -> Page:
    temp_game = Game(name,[],True,"","",date)
    if color == "Black":
        temp_game.is_white = False    
    state.current_game = temp_game
    return add_move(state)
        
    
@route
def add_move(state: State) -> Page:
    if state.current_game.is_white:
        first = "Your Move: "
        second = "Opoonent Move: "
    else:
        second = "Your Move: "
        first = "Opoonent Move :"
    return Page(state, [add_description, "\n",
        "Moves:\n", 
        str(list_moves(state.current_game.moves)), Button("Back", "back", Argument("page","home")), "\n",
        first, TextBox("first_move"), Button("Add","update_moves"), "\n",
        second, TextBox("second_move"), Button("Stop Inputting","declare_result")
        ])

    
@route
def update_moves(state: State, first_move: str, second_move: str) -> Page:
    if legal_notation(first_move.strip()) and legal_notation(second_move.strip()) and first_move.strip() != "...":
        if second_move.strip() == "...":
            second_move = ""
        combined_move = first_move.strip() + "|" + second_move.strip()
        state.current_game.moves.append(combined_move)
        return add_move(state)
    else:
        return Page(state,["Invalid Notation, Try Again", Button("Ok","add_move")])

@route
def declare_result(state: State) -> Page:
    return Page(state, [
        "Game Outcome: " , RadioButtonGroup("outcome",["Win","Loss","Draw", "Incomplete"],"Win"), "\n",
        "Reasoning: ", SelectBox("reason", ["Checkmate","Timeout","Resignation","Abandonment",
                                            "Stalemate", "Insufficient Material","Three-Fold Repetition",
                                            "50/75 Move Rule", "Mutual Agreement"]), "\n",
        Button("Finish","add_library")
        ])

@route
def add_library(state:State, outcome: str, reason: str) -> Page:
    state.current_game.results = outcome
    state.current_game.result_factor = reason
    state.library.append(state.current_game)
    return index(state)

@route
def game_library(state: State) -> Page:
    organized_library = sort_games(state.sort_option,filter_games(state.search_term,state.search_type,state.library))
    game_buttons = []
    for game_index, game in enumerate(organized_library):
        game_buttons.append(Button(game.opponent, "library_select",Argument("selected_index", game_index)))
    return Page(state,
           ["Search Term:", TextBox("term"), SelectBox("type",["Opponent", "Date","General Outcome"]),
          Button("Search", "update_sorting"), "\n",
           "Filter By: ", SelectBox("sort",["Earliest", "Latest", "Num. of Moves", "Opponent"], state.sort_option), Button("Stats","library_stats"), "\n",
           Button("Back", "back", Argument("page","home")), "\n"]
           + game_buttons)

        
        
   
  
@route
def update_sorting(state: State, term: str, type: str, sort: str) -> Page:
    state.sort_option = sort
    state.search_term = term
    state.search_type = type
    return game_library(state)

@route
def library_select(state: State, selected_index: int) -> Page:
    organized_library = sort_games(state.sort_option,filter_games(state.search_term,state.search_type,state.library))
    state.current_game = organized_library[selected_index]
    game_select = state.current_game
    color = "Black"
    if game_select.is_white:
        color = "White"
    return Page(state,[Button("Back", "back", Argument("page","library")), "\n",
                       "Opponent: ", game_select.opponent, "\n"
                       "Date: ", game_select.date, "\n",
                       "Color:", color, "\n",
                       "Outcome: ", game_select.results, "---", game_select.result_factor, "\n",
                       "Moves:", "\n",
                       str(list_moves(game_select.moves))
                          ])
@route
def library_stats(state: State)-> Page:
    total = 0
    for game in state.library:
        total += 1
    if not total:
        return Page(state, ["No Games Played!"], Button("Back","back", Argument("page","library")))
    results = result_stats(state.library)
    wins = results[0]
    losses = results[1]
    draws = results[2]
    incompletes = results[3]
    return Page(state,["Total Games: ", total, "\n",
                       "Completed Games: ", total - incompletes, "\n",
                       "Inompleted Games: ", incompletes, "\n",
                       "Wins: ", wins, "\n",
                       "Losses: ", losses, "\n",
                       "Draws: ", draws, "\n",
                       "Win percentage: ", (100*wins)/(total-incompletes), "%"])

    
    
    
test_library = [
    Game(
        opponent="Alice",
        moves=["e4|e5", "Nf3|O-O", "Nc6|Bb5#"],
        is_white=True,
        results="Win",
        result_factor="Checkmate",
        date="2026-11-15"
    ),
    Game(
        opponent="Bob",
        moves=["d4|Nf6", "c4|g6", "Nc3|Ng4"],
        is_white=False,
        results="Loss",
        result_factor="Timeout",
        date="2026-11-14"
    ),
    Game(
        opponent="Charlie",
        moves=["e4|c5", "Nf3|d6", "d4|"],
        is_white=True,
        results="Draw",
        result_factor="Stalemate",
        date="2026-11-12"
    ),
     Game(
        opponent="Patrick",
        moves=["e4|K5", "O-O-O|d6", "d4#|"],
        is_white=False,
        results="Incomplete",
        result_factor="Abandonment",
        date="2006-01-02"
    )
]

start_server(State(test_library,Game("",[],True,"","",""),"","",""))
