# mpudata.py
class MPUData:
    def __init__(self, ax, ay, az, rx, ry, rz):
        self.ax = ax
        self.ay = ay
        self.az = az
        self.rx = rx
        self.ry = ry
        self.rz = rz

    def __repr__(self):
        return f"MPUData(ax={self.ax}, ay={self.ay}, az={self.az}, rx={self.rx}, ry={self.ry}, rz={self.rz})"