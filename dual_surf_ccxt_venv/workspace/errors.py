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

class UpdateStackError(Exception):
    def __init__(self):
        super().__init__('UpdateStack Refetching Error, immediately enter with root for cleaning position yourself!')


#레버리지 관련 에러 추후 업데이트 및 보강, 단순 메시지 말고 레버리지 변경 등의 고려사항 필요.
class LeverageError(Exception):
    def __init__(self):
        super().__init__('Leverage exceeding Error, immediately enter with root for cleaning position yourself!')
#마진 부족 관련 에러 추후 업데이트 및 보강, 단순 메시지 말고 레버리지 변경 등의 고려사항 필요.
class InsufficientError(Exception):
    def __init__(self):
        super().__init__('Margin Sufficient Error, immediately enter with root for cleaning position yourself!')