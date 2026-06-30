import 'package:app1/features/recommendation_export/data/recommendation_pdf_service.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  // Test case references: documents/Testfaelle_Frontend.md#t12-pdf-export
  test('übersetzt das biologische Geschlecht für die PDF-Ausgabe', () {
    expect(biologicalSexLabelForPdf('male'), 'männlich');
    expect(biologicalSexLabelForPdf('female'), 'weiblich');
    expect(biologicalSexLabelForPdf(null), 'Keine Angabe');
  });
}
