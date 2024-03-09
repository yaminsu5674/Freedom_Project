import pprint

class LeverageError(Exception):
    def __init__(self):
        super().__init__('Leverage is not initialized. Program will close.')

class BalanceError(Exception):
    def __init__(self):
        super().__init__('Balance is not clean. Program will close.')

class ProgramEndError(Exception):
    def __init__(self):
        super().__init__('On agree of User, Program will close.')