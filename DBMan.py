import sqlite3


def dict_factory(cursor, row):
	dict_ = {}
	for idx, col in enumerate(cursor.description):
		dict_[col[0]] = row[idx]
	return dict_

def connect(self, apply_row_factory=True):
	self.con = sqlite3.connect(database=self.name)
	if apply_row_factory:
		self.con.row_factory = dict_factory
	self.cur = self.con.cursor()

class osuDB:
	def __init__(self, database, apply_row_factory=True):
		self.name = database

		self.connection = sqlite3.connect(database=self.name)
		if apply_row_factory:
			self.connection.row_factory = dict_factory
		self.cursor = self.connection.cursor()

	def __repr__(self):
		return f"{self.__class__.__name__}({self.name})"

	def commit(self):
		return self.connection.commit()

	def execute(self, *args, **kwargs):
		return self.cursor.execute(*args, **kwargs)

	def executemany(self, *args, **kwargs):
		return self.cursor.executemany(*args, **kwargs)

	def fetchall(self):
		return self.cursor.fetchall()

	def fetchone(self):
		return self.cursor.fetchone()

if __name__ == "__main__":
	db = osuDB('./testing/db.sqlite3')
	db.execute()