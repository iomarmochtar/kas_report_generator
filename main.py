import json
import os
import datetime
import pickle
import base64
import tempfile
import sys
from typing import Dict, List, Any
from pprint import pprint
from cakap.decorators import auth, chelp
from cakap.base import BotBase
from cakap.utils import Utils as bot_utils
from dotenv import load_dotenv
from kas_report_generator.data_provider.gsheet import GSheet
from kas_report_generator.data_provider import utils
from kas_report_generator.printer.pdf import PDF

class Config(object):
    def __init__(self):
        load_dotenv()

    def __conf(self, key: str, default: Any='', mandatory: bool = False) -> Any:
        val = os.environ.get(key, default)
        if mandatory and not val:
            print(f'You must set config {key} !!!')
            sys.exit(1)
        return val

    @property
    def footer_left(self) -> str:
        return self.__conf('FOOTER_LEFT')

    @property
    def footer_right(self) -> str:
        return self.__conf('FOOTER_RIGHT')

    @property
    def report_title(self) -> str:
        return self.__conf('REPORT_TITLE', default='Laporan KAS GLS')

    @property
    def blacklist(self) -> List[str]:
        return self.__conf('RUMAH_BLACKLIST').split(',')

    @property
    def begin_rekap(self) -> datetime.date:
        return utils.gen_date(month=6, year=2018) 

    @property
    def bot_token(self) -> str:
        return self.__conf('BOT_TOKEN', mandatory=True)

    @property
    def bot_admins(self) -> List[str]:
        return self.__conf('BOT_ADMIN').split(',')

    @property
    def gsheet_id(self) -> str:
        return self.__conf('GSHEET_ID', mandatory=True)

    @property
    def gsheet_cellrange(self) -> str:
        return self.__conf('GSHEET_CELLRANGE', mandatory=True)

    @property
    def gsheet_sa(self) -> Dict[str, Any]:
        val = self.__conf('GSHEET_SA', mandatory=True)
        result = base64.b64decode(val.encode())
        return json.loads(result)

class GLSBot(BotBase):
    def __init__(self, config, *args, **kwargs):
        self.config: Config = config 
        super().__init__(token=self.config.bot_token, 
                         users=self.config.bot_admins,
                         *args, **kwargs)

    @auth
    def cmd_genreport(self, bot, update):
        user_info: Dict[str, Any] = bot_utils.user_details(update)

        self.logger.info(f'{user_info} is generating reports')
        bot_utils.send(bot, update, 'Generating, please wait ...', reply=True)

        now: datetime.datetime = utils.now()
        rekap_kas: Dict[str, Any] = self.gsheet.rekap_kas(self.config.begin_rekap, self.config.blacklist)

        generated_at = now.strftime('%d-%m-%Y %H:%M:%S')
        variables: Dict[str, Any] = { 
                        'rekaps': rekap_kas,
                        'footer_left': self.config.footer_left,
                        'footer_right': self.config.footer_right,
                        'generated_at': generated_at,
                        'months': utils.range_prev_months(utils.now_date(now).replace(day=1), 2),
                        'title': self.config.report_title
                    }
        temp_dest: str = tempfile.mktemp()
        filename: str = f'laporan_kas_{generated_at}.pdf'
        self.logger.info(f'Writing to temporary destination {temp_dest}')
        PDF.write(temp_dest, variables)

        self.logger.info(f'Sending report by filename {filename}')
        bot_utils.send_doc(bot, update, temp_dest, filename)
        os.remove(temp_dest)

    @property
    def gsheet(self) -> GSheet :
        return GSheet(credentials=self.config.gsheet_sa, 
                      spreadsheet_id=self.config.gsheet_id,
                      cell_range=self.config.gsheet_cellrange)


if __name__ == '__main__':
    bot: GLSBot = GLSBot(config=Config())
    bot.main()