from binascii import unhexlify, hexlify
from pycrate_mobile import *
from pycrate_mobile.NAS import *
from abc import ABC, ABCMeta, abstractmethod
from CryptoMobile.Milenage import Milenage
from CryptoMobile.Milenage import make_OPc
from CryptoMobile.conv import *
from CryptoMobile.ECIES import *
from pycrate_mobile.TS24501_IE import *

def byte_xor(ba1, ba2):
    """ XOR two byte strings """
    return bytes([_a ^ _b for _a, _b in zip(ba1, ba2)])

AUTN=b'44c3e03b5a5980006e85505b4843ceee'
OP = b'E8ED289DEBA952E4283B54E88E6183CA'
# 63 bf a5 e e6 52 33 65 ff 14 c1 f4 5f 88 73 7d 
OP = unhexlify(OP)
key = b'465B5CE8B199B49FAA5F0A2EE238A6BC'
# c a 34 60 1d 4f 7 67 73 3 65 2c 4 62 53 5b 
key = unhexlify(key)
sqn_xor_ak =  b'44c3e03b5a59'
sqn_xor_ak = unhexlify(sqn_xor_ak)
amf =  b'8000'
amf = unhexlify(amf)
mac =  b'6e85505b4843ceee'
mac = unhexlify(mac)
rand =  b'84b692e300a6513590940b39a35a97f4'
rand = unhexlify(rand)
abba =  b'0000'
abba = unhexlify(abba)
supi = b'999700000000001'

print("Creating Auth keys")
Mil = Milenage(OP)
# Mil.set_opc(make_OPc(key, OP))
Mil.set_opc(OP)
AK = Mil.f5star(key, rand)
print("AK: ", hexlify(AK))

SQN = byte_xor(AK, sqn_xor_ak)
# SQN = b'000000000600'
# SQN = unhexlify(SQN)
print("SQN: ", hexlify(SQN))

Mil.f1(key, rand, SQN=SQN, AMF=amf)
RES, CK, IK, AK  = Mil.f2345(key, rand)
print("RES: ", hexlify(RES))
print("CK: ", hexlify(CK))
print("IK: ", hexlify(IK))
print("AK: ", hexlify(AK))


sn_name = b"5G:mnc070.mcc999.3gppnetwork.org"
Res = conv_501_A4(CK, IK, sn_name, rand, RES)
print("Res: ", hexlify(Res))

# Get K_AUSF
k_ausf = conv_501_A2(CK, IK, sn_name, sqn_xor_ak)
print("K_AUSF: ", hexlify(k_ausf))
# Get K_SEAF
k_seaf = conv_501_A6(k_ausf, sn_name)
print("K_SEAF: ", hexlify(k_seaf))
# Get K_AMF
k_amf = conv_501_A7(k_seaf, supi, abba)
print("K_AMF: ", hexlify(k_amf))
# Get K_NAS_ENC
k_nas_enc = conv_501_A8(k_amf, alg_type=1, alg_id=1)
# Get least significate 16 bytes from K_NAS_ENC 32 bytes
k_nas_enc = k_nas_enc[16:]
print("K_NAS_ENC: ", hexlify(k_nas_enc))
# Get K_NAS_INT
k_nas_int = conv_501_A8(k_amf, alg_type=2, alg_id=2)
k_nas_int = k_nas_int[16:]
# k_nas_int = unhexlify('fbf4bfd78c4fe1a4dca0caabc49047f6')
print("K_NAS_INT: ", hexlify(k_nas_int))

nas_pdu = "7e021c73f02a027e00670100152e0101c1ffff91a12801007b000780000a00000d00120181220101250908696e7465726e6574"

print("..................Decoding EURANSIM generate msg...................")
EncMsg, e = parse_NAS5G(unhexlify(nas_pdu))
print(".......................Enc Message...............................")
print(EncMsg.show())
print(".......................Enc Message...............................")

# EncMsg.decrypt(key=k_nas_enc, dir=0, fgea=1, seqnoff=0, bearer=1)

# print(".......................MAC Message...............................")
# print(EncMsg.mac_verify(key=k_nas_int, dir=0, fgia=2, seqnoff=0x10, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=0, fgia=2, seqnoff=0, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=0, fgia=2, seqnoff=1, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=0, fgia=2, seqnoff=2, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=0, fgia=2, seqnoff=3, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=0, fgia=2, seqnoff=4, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=0, fgia=2, seqnoff=5, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=0, fgia=2, seqnoff=6, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=0, fgia=2, seqnoff=7, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=0, fgia=2, seqnoff=8, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=0, fgia=2, seqnoff=9, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=0, fgia=2, seqnoff=10, bearer=1))

# print("---------------------")
# print(EncMsg.mac_verify(key=k_nas_int, dir=1, fgia=2, seqnoff=0x10, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=1, fgia=2, seqnoff=0, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=1, fgia=2, seqnoff=1, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=1, fgia=2, seqnoff=2, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=1, fgia=2, seqnoff=3, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=1, fgia=2, seqnoff=4, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=1, fgia=2, seqnoff=5, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=1, fgia=2, seqnoff=6, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=1, fgia=2, seqnoff=7, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=1, fgia=2, seqnoff=8, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=1, fgia=2, seqnoff=9, bearer=1))
# print(EncMsg.mac_verify(key=k_nas_int, dir=1, fgia=2, seqnoff=10, bearer=1))
# print(".......................MAC Message...............................")

print(EncMsg.mac_verify(key=k_nas_int, dir=0, fgia=2, seqnoff=0, bearer=1))

EncMsg.decrypt(key=k_nas_enc, dir=0, fgea=1, seqnoff=0, bearer=1)

print(".......................Dec Message...............................")
print(hexlify(EncMsg._dec_msg))
print(".......................Dec Message...............................")

DecMsg, e = parse_NAS5G(EncMsg._dec_msg)
print(e)
print(".......................Dec Message...............................")
# print(DecMsg.show())
print(".......................Dec Message...............................")

k_nas_enc = conv_501_A8(k_amf, alg_type=1, alg_id=1)
k_nas_enc = k_nas_enc[16:]
print("K_NAS_ENC: ", hexlify(k_nas_enc))
EncMsg.decrypt(key=k_nas_enc, dir=0, fgea=1, seqnoff=0, bearer=1)
DecMsg, e = parse_NAS5G(EncMsg._dec_msg)
print("error ", e)
print(DecMsg.show())
print(DecMsg.get_val_d())

k_nas_enc = conv_501_A8(k_amf, alg_type=1, alg_id=2)
k_nas_enc = k_nas_enc[16:]
print("K_NAS_ENC: ", hexlify(k_nas_enc))
EncMsg.decrypt(key=k_nas_enc, dir=0, fgea=2, seqnoff=0, bearer=1)
DecMsg, e = parse_NAS5G(EncMsg._dec_msg)
print("error ", e)

k_nas_enc = conv_501_A8(k_amf, alg_type=1, alg_id=0)
k_nas_enc = k_nas_enc[16:]
print("K_NAS_ENC: ", hexlify(k_nas_enc))
EncMsg.decrypt(key=k_nas_enc, dir=0, fgea=0, seqnoff=0, bearer=1)
DecMsg, e = parse_NAS5G(EncMsg._dec_msg)
print("error ", e)
