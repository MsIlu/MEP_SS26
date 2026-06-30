// Created as part of the authentication and profile management implementation.
// Defines the frontend account model returned by the backend.

class Account {
  /// Public account data returned by the backend.
  final int id;
  final String email;

  const Account({required this.id, required this.email});

  factory Account.fromJson(Map<String, dynamic> json) {
    return Account(id: json['id'] as int, email: json['email'] as String);
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
    };
  }
}