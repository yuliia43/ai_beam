class State:
	leftbank = []
	boat = {'position': 'left', 'passengers': []}
	rightbank = []
	value = 0
	prev_state = None           #saving for the final output

	def __init__(self, leftbank=[], rightbank = [],\
				 boat = {'position': 'right', 'passengers': []}, value = 0):
		self.leftbank = leftbank
		self.rightbank = rightbank
		self.boat = boat
		self.value = value
		self.prev_state = None

	def __eq__(self, another):
		if self is None or another is None: 
			return another is None and self is None
		else:
			return self.leftbank == another.leftbank and self.boat['passengers'] == another.boat['passengers']

	def __lt__(self, another):
		return self.value < another.value


class Task:
	begin_state = None
	final_state = None
	illegal_pairs = []      #pairs that can't be on bank together without farmer
	boat_states = {}        #possible states in boat wit quantity more than 2


	def __init__(self, begin_state = State(leftbank = ['lion', 'fox', 'goose', 'corn']),\
					final_state = State(rightbank = ['lion', 'fox', 'goose', 'corn']),\
					illegal_pairs =(('lion', 'fox'),('fox', 'goose'), ('goose', 'corn')),\
					boat_states = (['goose', 'corn'], ['fox', 'corn'])):
		self.begin_state = begin_state
		self.final_state = final_state
		self.illegal_pairs = illegal_pairs
		self.boat_states = boat_states
		


class BeamAlgoBuilder:
	task = None
	k=0                      #number of beams
	final_bank=''            #bank to which passengers will be moved

	def __init__(self, task=Task(), k=3):
		self.task = task
		self.k = k
		if task.begin_state.leftbank>task.final_state.leftbank:
			self.final_bank = 'right'
		else:
			self.final_bank = 'left'

	def find_next_states(self, state):
		next_states = []
		self.search_for_next_states(state, next_states)
		for next_state in next_states:
			next_state.prev_state = state
		return next_states


	def search_for_next_states(self, state, next_states):
		position = state.boat['position']
		if position == 'right':
			bank = state.leftbank.copy()
		else:
			bank = state.rightbank.copy()
		for passenger in state.boat['passengers']:
			bank.append(passenger)                   #reallocates all pasengers to the bank
		for passenger in bank:
			boat_state = [passenger]
			self.append_state(state, bank, boat_state, next_states, position)
		for boat_state in self.task.boat_states:
			able = True
			for psngr in boat_state:
				if not psngr in bank:
					able = False
					break
			if able:
				self.append_state(state, bank, boat_state, next_states, position)
		self.append_state(state, bank, [], next_states, position)

	def append_state(self, state, bank, boat_state, next_states, bankstr):
		value = 0                                #estimated value (w)
		main_bank = bank.copy()
		if bankstr == 'right':
			leftbank = main_bank
			rightbank = state.rightbank.copy()
			opposite_position = 'left'

		else:
			leftbank = state.leftbank.copy()
			rightbank = main_bank
			opposite_position = 'right'
		for passenger in boat_state:
			main_bank.remove(passenger)                      #removing passenger from the main bank array
			if self.should_be_on_bank(passenger, opposite_position):      #checking if passenger should be on bank
				value+=100  
		new_state = State(leftbank = leftbank, \
			boat = {'position': opposite_position, 'passengers': boat_state}, \
			rightbank = rightbank, value=value)
		self.incr_value_due_to_finalbank(new_state)
		if new_state == self.task.final_state:
				next_states.append(new_state)
		elif not self.has_illegal_pairs(main_bank):
			if new_state != state:
				next_states.append(new_state)

	def incr_value_due_to_finalbank(self, new_state):      #increments w on the quantity of creatures on the bank
		if self.final_bank=='left':                    
			new_state.value+=abs(len(new_state.rightbank)-len(self.task.final_state.rightbank))
		else:                    
			new_state.value+=abs(len(new_state.leftbank)-len(self.task.final_state.leftbank))

	def should_be_on_bank(self, passenger, bank):
		if bank == 'right':
			return passenger in self.task.final_state.rightbank
		else:
			return passenger in self.task.final_state.leftbank


	def has_illegal_pairs(self, bank):
		for illegal_pair in self.task.illegal_pairs:
			has_passenger1=False
			has_passenger2=False
			for passenger in bank:
				if passenger == illegal_pair[0]:
					has_passenger1 = True
				elif passenger == illegal_pair[1]:
					has_passenger2 = True

				if has_passenger1 and has_passenger2:
					return True
		return False

	#Traditional BEAM algorithm gets k random states as the first step. 
	#Since my task has concrete begin state, I skipped that step. 
	#Value of k is set as 3 by default, but can be changed by the user
	def BEAM(self):            
		states = [self.task.begin_state]
		while not self.contains_final_state(states):
			new_states = list()
			for state in states:
				new_states += self.find_next_states(state)
			new_states.sort()
			states = new_states[:self.k]


	def contains_final_state(self, states):
		for state in states:
			if state == self.task.final_state:
				self.task.final_state.prev_state = state.prev_state
				return True
		return False    


def print_states(states):
	for state in states:
		print ('|' + str(state.leftbank) + '|' + str(state.boat) + '|' + str(state.rightbank) +'|' + str(state.value))



builder = BeamAlgoBuilder(k=2)
builder.BEAM()
state = builder.task.final_state
state_str = ''
while state != None:
	state_str = '|{:^35}|{:^35}|{:^35}|\n'.format(str(state.leftbank), str(state.boat['passengers']), str(state.rightbank))\
				+state_str
	state = state.prev_state
state_str = '|{:^35}|{:^35}|{:^35}|\n'.format('left bank', 'boat', 'right bank') \
			+ '_'*109 + '\n' + state_str

print(state_str)