import 'package:encrypt/encrypt.dart';
class EncryptionService {
  static final key = Key.fromUtf8('my_ultra_secure_key_32_characters_'); // 실제 운영시는 env 처리 권장
  static final iv = IV.fromLength(16);
  static final encrypter = Encrypter(AES(key));
  static String encrypt(String t) => encrypter.encrypt(t, iv: iv).base64;
}
