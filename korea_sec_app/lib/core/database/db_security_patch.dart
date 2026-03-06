class DBSecurityPatch {
  static String sanitize(String input) => input.replaceAll(RegExp(r"[<>;'\"--]"), '');
}
