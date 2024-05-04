self.df['floor'] = (self.df.floor.str.replace('همکف', '0').replace('زیرهمکف', '-1').replace('از بیشتر از', '').replace('+۳۰', '۳۰'))
self.df['floor'] = self.df.floor.str.replace('همکف', '0').replace('زیرهمکف', '-1').replace('', 'از بیشتر از').replace('+۳۰', '۳۰')
