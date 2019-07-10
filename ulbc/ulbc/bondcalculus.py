import pexpect


BOND_DIRECTORY = "~/Documents/PhD/bondwb"


class BondwbException(Exception):
    pass


class BondModel(object):
    def __init__(self, modelfile : str):
        self._bondwb = pexpect.spawn('stack exec bondwb',
                                     cwd="/home/twright/Documents/PhD/bondwb")
        self._expect()
        self._load(modelfile)

    def _expect(self):
        self._bondwb.expect('BioWB:> ')

    def _load(self, filename):
        self._bondwb.sendline('load {}')
        self._bondwb.expect('BioWB:> ')

    def __del__(self):
        del self._bondwb


class BondProcess(object):
    def __init__(self, _expr : str, model : BondModel):
        pass