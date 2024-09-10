#!/usr/bin/env python3

import sys, requests, emoji, json, pickle

from bitcoin import SelectParams
from bitcoin.wallet import CBitcoinAddress, CBitcoinSecret
from bitcoin.core import b2x, lx, COutPoint, CMutableTxOut, CMutableTxIn, CMutableTransaction
from bitcoin.core.script import CScript, OP_DUP, OP_IF, OP_ELSE, OP_ENDIF, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG, SignatureHash, SIGHASH_ALL, OP_FALSE, OP_DROP, OP_CHECKLOCKTIMEVERIFY, OP_SHA256

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from fake_http_header import FakeHttpHeader
from pathlib import Path

NETWORK = str('mainnet') # set network (mainnet/testnet)
VERSION = str('v0.1.2-beta') # current version
VERIFICATIONBLOCKHEIGHT = str('00000000000000000002a1644fc407b6ae2f899ff52fb30280ced25d70277348') # 859975

class BTCScript():
    def __init__(self, net: str = NETWORK):
        self.params = SelectParams(net)

    def get_redeem_script(self, blocks: int, hashed_preimage: str, sender_address: str, receiver_address: str) -> list:
        self.redeem_script = CScript([OP_IF,
                                        OP_SHA256, hashed_preimage, OP_EQUALVERIFY,
                                        OP_DUP, OP_HASH160, receiver_address,
                                    OP_ELSE,
                                        blocks, OP_CHECKLOCKTIMEVERIFY, OP_DROP,
                                        OP_DUP, OP_HASH160, sender_address,
                                    OP_ENDIF,
                                    OP_EQUALVERIFY,
                                    OP_CHECKSIG]
        )

        self.script_pubkey = self.redeem_script.to_p2sh_scriptPubKey()
        self.p2sh_address = CBitcoinAddress.from_scriptPubKey(self.script_pubkey)
        return [blocks, b2x(self.redeem_script), self.p2sh_address, self.redeem_script]

    def refund(self, txid: str, vout: int, amount: int, fee_per_byte: int, address: str, redeem_blockheight: int, redeem_script: str, privkey: str, vsize = int(320)) -> list:
        final_fee = int(vsize * fee_per_byte)
        privkey = CBitcoinSecret(privkey)
        self.txid = lx(txid)
        self.txin = CMutableTxIn(COutPoint(self.txid, vout))
        self.txin.nSequence = 0
        self.txout = CMutableTxOut(amount - final_fee, address.to_scriptPubKey())
        self.tx = CMutableTransaction([self.txin], [self.txout])
        self.tx.nLockTime = redeem_blockheight
        self.sighash = SignatureHash(redeem_script, self.tx, 0, SIGHASH_ALL)
        self.sig = privkey.sign(self.sighash) + bytes([SIGHASH_ALL])
        self.txin.scriptSig = CScript([self.sig, privkey.pub, OP_FALSE, redeem_script])
        self.refund_hex = b2x(self.tx.serialize())
        return [self.refund_hex, self.tx, final_fee]

class Output(QWidget):
    def __init__(self, **kwargs):
        super(Output, self).__init__()

        # get image path
        _image_path = f'{Path().absolute()}/atomicmixer/images'

        self._output_start = True if 'start' in kwargs  and kwargs['start'] else False
        self._output_refund_data = True if 'output_refund_data' in kwargs and kwargs['output_refund_data'] else False
        self._output_refund_txid = True if 'output_refund_txid' in kwargs and kwargs['output_refund_txid'] else False

        self.btc_logo_black = QLabel('BTC_BLACK')
        self.btc_logo_black.setStyleSheet("color: blue; font: bold")
        self.btc_logo_black.setAlignment(Qt.AlignCenter)
        self.btc_logo_black.setPixmap(QPixmap(f"{_image_path}/bitcoin_black.png").scaled(300,300))

        self.btc_logo_orange = QLabel('BTC_ORANGE')
        self.btc_logo_orange.setStyleSheet("color: blue; font: bold")
        self.btc_logo_orange.setAlignment(Qt.AlignCenter)
        self.btc_logo_orange.setPixmap(QPixmap(f"{_image_path}/bitcoin.png").scaled(200,200))

        self.arrow = QLabel('ARROW')
        self.arrow.setStyleSheet("color: blue; font: bold")
        self.arrow.setAlignment(Qt.AlignCenter)
        self.arrow.setPixmap(QPixmap(f"{_image_path}/arrow.png").scaled(130,130))

        if self._output_refund_data:
            self._refund_data = kwargs
            self.output_refund()

        if self._output_refund_txid:
            self._refund_txid = kwargs
            self.output_refund_txid()

        if self._output_start:
            self.output_start()

    def output_start(self):
        self.header = QLabel('WELCOME TO THE ATOMICMIXER REFUND TOOL!\n')
        font = self.header.font()
        font.setPointSize(13)
        self.header.setFont(font)
        self.header.setStyleSheet("color: lightgreen; font: bold")
        self.header.setAlignment(Qt.AlignCenter)

        self.footer = QLabel(f'NO SHADY TOKEN {emoji.emojize(":check_mark:")} NO REGISTRATION {emoji.emojize(":check_mark:")} OPEN SOURCE {emoji.emojize(":check_mark:")}')
        font = self.footer.font()
        font.setPointSize(13)
        self.footer.setFont(font)
        self.footer.setStyleSheet("color: lightgreen")
        self.footer.setAlignment(Qt.AlignCenter)

        layout = QGridLayout()
        layout.addWidget(self.header, 0, 0, 1, 0)
        layout.addWidget(self.btc_logo_black, 1, 0)
        layout.addWidget(self.arrow, 1, 1)
        layout.addWidget(self.btc_logo_orange, 1, 2)
        layout.addWidget(self.footer, 2, 0, 1, 0)
        self.setLayout(layout)

    def output_refund(self):
        self.header = QLabel('YOUR REFUND DATA:\n')
        font = self.header.font()
        font.setPointSize(13)
        self.header.setFont(font)
        self.header.setStyleSheet("color: lightgreen; font: bold")
        self.header.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.body_left = QLabel('\nREFUND ADDRESS: \n AMOUNT: \n REFUND BLOCKHEIGHT: \n HTLC ADDRESS: ')
        font = self.body_left.font()
        font.setPointSize(12)
        self.body_left.setFont(font)
        self.body_left.setStyleSheet("color: #E5E5E5")
        self.body_left.setAlignment(Qt.AlignRight)

        _refund_data = f"\n {self._refund_data['_refund_data']['sending_address']}\n {self._refund_data['_refund_data']['funding_amount']:,}\n {self._refund_data['_refund_data']['refund_blockheight']:,}\n {self._refund_data['_refund_data']['htlc_address']}"
        self.body_right = QLabel(_refund_data)
        font = self.body_right.font()
        font.setPointSize(12)
        self.body_right.setFont(font)
        self.body_right.setStyleSheet("color: lightgreen;")
        self.body_right.setAlignment(Qt.AlignLeft)
        self.body_right.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout = QGridLayout()
        layout.addWidget(self.header, 0, 0, 1, 0)
        layout.addWidget(self.btc_logo_black, 1, 0)
        layout.addWidget(self.arrow, 1, 1)
        layout.addWidget(self.btc_logo_orange, 1, 2)
        layout.addWidget(self.body_left, 2, 0)
        layout.addWidget(self.body_right, 2, 1, 1, 2)
        self.setLayout(layout)

    def output_refund_txid(self):
        self.header = QLabel(f'SUCCESS!\n\n TxId: {self._refund_txid["_refund_txid"]}')
        font = self.header.font()
        font.setPointSize(12)
        self.header.setFont(font)
        self.header.setStyleSheet("color: lightgreen; font: bold")
        self.header.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.header.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        layout = QGridLayout()
        layout.addWidget(self.header, 0, 0, 1, 0)
        layout.addWidget(self.btc_logo_black, 1, 0)
        layout.addWidget(self.arrow, 1, 1)
        layout.addWidget(self.btc_logo_orange, 1, 2)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle(f"AtomicMixer Refund Tool {VERSION}")
        self.setFixedWidth(800)
        self.setFixedHeight(500)
        self.setStyleSheet('color: white; background-color: #535353')
        self.center()

        # get absolute path
        self._curr_path = Path().absolute()

        # init btc script
        self._handle_btc = BTCScript()

        # buttons
        self.button1 = QPushButton("LOAD REFUND FILE")
        self.button1.setStyleSheet('color: white; background-color: green; font: bold; padding: 0.3em')
        self.button1.clicked.connect(self.load_refund)

        self.button2 = QPushButton("EXIT")
        self.button2.setStyleSheet('color: white; background-color: darkred; font: bold; padding: 0.3em')
        self.button2.clicked.connect(lambda: self.close())

        # layout
        layout = QGridLayout()
        layout.addWidget(Output(start = True), 0, 0, 1, 0)
        layout.addWidget(self.button1, 1, 0)
        layout.addWidget(self.button2, 1, 1)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def load_refund(self):
        # select file
        self._refund_file = self.load_refund_dialog()

        try:
            _lswp = open(f'{self._refund_file}', 'rb')
            _sending_address = pickle.load(_lswp)
            _receiving_address = pickle.load(_lswp)
            _funding_txid = pickle.load(_lswp)
            _funding_vout = pickle.load(_lswp)
            _funding_amount = pickle.load(_lswp)
            _secret_hex = pickle.load(_lswp)
            _refund_blockheight = pickle.load(_lswp)
            _htlc_address = pickle.load(_lswp)
            _lswp.close()

            self._refund_data = {
                'sending_address': _sending_address,
                'receiving_address': _receiving_address,
                'funding_txid': _funding_txid,
                'funding_vout': _funding_vout,
                'funding_amount': _funding_amount,
                'secret_hex': _secret_hex,
                'refund_blockheight': _refund_blockheight,
                'htlc_address': _htlc_address,
            }
        except Exception as ex:
            self._refund_data = False

        if self._refund_data:
            self.button1 = QPushButton("REFUND")
            self.button1.setStyleSheet('color: white; background-color: green; font: bold; padding: 0.3em')
            self.button1.clicked.connect(self.get_privkey)

            self.button2 = QPushButton("EXIT")
            self.button2.setStyleSheet('color: white; background-color: darkred; font: bold; padding: 0.3em')
            self.button2.clicked.connect(lambda: self.close())

            layout = QGridLayout()
            layout.addWidget(Output(output_refund_data = True, _refund_data = self._refund_data), 0, 0, 1, 0)
            layout.addWidget(self.button1, 1, 0)
            layout.addWidget(self.button2, 1, 1)

            widget = QWidget()
            widget.setLayout(layout)
            self.setCentralWidget(widget)
        else:
            self.error_box()

    def get_privkey(self):
        _privkey, ok_pressed = QInputDialog.getText(self, "Enter your privkey","PLEASE ENTER YOUR PRIVATE KEY:", QLineEdit.Password, "")
        if ok_pressed and _privkey != '':
            self.create_refund(_privkey)
        else:
            _okBox = QMessageBox()
            _okBox.setIcon(QMessageBox.Information)
            _okBox.setWindowTitle("INFO")
            _okBox.setStandardButtons(QMessageBox.Ok)
            _okBox.setStyleSheet('color: white; background-color: red; font: bold')
            _okBox.setText("< p align = 'center'>PLEASE ENTER YOUR PRIVATE KEY!</p>")
            _res = _okBox.exec()

    def create_refund(self, privkey: str):
        # mempool api endpoints
        if NETWORK == "testnet":
            _fee_url = "https://mempool.space/testnet/api/v1/fees/recommended"
            _blockheight_url = "https://mempool.space/testnet/api/blocks/tip/height"
            _broadcast_url = "https://mempool.space/testnet/api/tx"
        else:
            _fee_url = "https://mempool.space/api/v1/fees/recommended"
            _blockheight_url = "https://mempool.space/api/blocks/tip/height"
            _broadcast_url = "https://mempool.space/api/tx"

        try:
            # generate random headers
            _fake_header = FakeHttpHeader(domain_name = 'uk')
            _header = _fake_header.as_header_dict()

            # get current fees
            _res_fee = requests.get(url = _fee_url, headers = _header, timeout = 20)
            _res_fee = _res_fee.json()
            _fee_per_byte = _res_fee['fastestFee']

            # get current blockheight
            _res_blockheight = requests.get(url = _blockheight_url, headers = _header, timeout = 20)
            _current_blockheight = _res_blockheight.json()

            # prepare addresses
            _clean_sender_address = CBitcoinAddress(self._refund_data['sending_address'])
            _clean_receiver_address = CBitcoinAddress(self._refund_data['receiving_address'])

            # get redeem script
            _preimage_bytes = bytes.fromhex(self._refund_data['secret_hex'])
            _btc_redeem_script = self._handle_btc.get_redeem_script(self._refund_data['refund_blockheight'], _preimage_bytes, _clean_sender_address, _clean_receiver_address)

            # generate refund tx
            _btc_refund = self._handle_btc.refund(self._refund_data['funding_txid'], self._refund_data['funding_vout'], self._refund_data['funding_amount'], _fee_per_byte, _clean_sender_address, self._refund_data['refund_blockheight'], _btc_redeem_script[3], privkey)

            # get blockheight diff
            _diff_blockheight = int(self._refund_data['refund_blockheight'] - _current_blockheight)

            if _diff_blockheight > 0:
                _okBox = QMessageBox()
                _okBox.setIcon(QMessageBox.Information)
                _okBox.setWindowTitle("INFO")
                _okBox.setStandardButtons(QMessageBox.Ok)
                _okBox.setStyleSheet('color: white; background-color: red; font: bold')
                _okBox.setText(f"< p align = 'center'>REFUND BLOCKHEIGHT NOT REACHED!</p><p>CURRENT BLOCKHEIGHT: {_current_blockheight:,}</p><p>DIFFERENCE: {_diff_blockheight} BLOCKS</p>")
                _res = _okBox.exec()
            else:
                _res_broadcast = requests.post(url = _broadcast_url, data = _btc_refund[0], headers = _header)
                _refund = _res_broadcast.text
                _refund_success = False if 'error' in _refund else True

                if _refund_success:
                    # exit button
                    self.button = QPushButton("EXIT")
                    self.button.setStyleSheet('color: white; background-color: darkred; font: bold; padding: 0.3em')
                    self.button.clicked.connect(lambda: self.close())

                    layout = QGridLayout()
                    layout.addWidget(Output(output_refund_txid = True, _refund_txid = _refund), 0, 0, 1, 0)
                    layout.addWidget(self.button, 1, 0)

                    widget = QWidget()
                    widget.setLayout(layout)
                    self.setCentralWidget(widget)
                else:
                    self.error_box()

        except Exception as ex:
            self.error_box()

    def load_refund_dialog(self):
        _options = QFileDialog.Options()
        _options |= QFileDialog.DontUseNativeDialog
        _refund_file, _ = QFileDialog.getOpenFileName(self,"SELECT WALLET", f"{self._curr_path}","All Files (*);;Python Files (*.py)", options = _options)

        if _refund_file:
            return _refund_file
        else:
            return False

    def error_box(self):
        _okBox = QMessageBox()
        _okBox.setIcon(QMessageBox.Information)
        _okBox.setWindowTitle("INFO")
        _okBox.setStandardButtons(QMessageBox.Ok)
        _okBox.setStyleSheet('color: white; background-color: red; font: bold')
        _okBox.setText(f"< p align = 'center'>SOMETHING WENT WRONG!")
        _res = _okBox.exec()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
