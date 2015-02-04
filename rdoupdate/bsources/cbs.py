from rdoupdate.bsources.koji_ import KojiSource


class CentOSBuidSystemSource(KojiSource):
    name = 'cbs'
    args = ['-p', 'cbs']
