"""
Phase 5 Execution Script
سكريبت تشغيل المرحلة الخامسة
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# إضافة المسار للملفات
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PHASE5_COMPREHENSIVE_INTEGRATION import Phase5ComprehensiveIntegrationManager

async def main():
    """الدالة الرئيسية لتشغيل المرحلة الخامسة"""
    try:
        print("🚀 بدء المرحلة الخامسة: التكامل والاختبار الشامل")
        print("=" * 60)
        
        # إنشاء مدير التكامل
        integration_manager = Phase5ComprehensiveIntegrationManager()
        
        # تنفيذ المرحلة الخامسة كاملة
        result = await integration_manager.execute_phase5_complete()
        
        if result['success']:
            print("\n✅ تم إكمال المرحلة الخامسة بنجاح!")
            print("\n📊 ملخص النتائج:")
            print("-" * 40)
            
            # عرض نتائج التكامل
            if 'integration' in result and result['integration']['success']:
                print("🔗 التكامل: ✅ ناجح")
                components = result['integration'].get('components', {})
                for comp_name, comp_result in components.items():
                    if comp_result.get('success'):
                        print(f"   - {comp_name}: ✅ نشط")
                    else:
                        print(f"   - {comp_name}: ❌ غير نشط")
            
            # عرض نتائج الاختبارات
            if 'testing' in result:
                test_results = result['testing']
                print("\n🧪 نتائج الاختبارات:")
                for category, tests in test_results.items():
                    print(f"   {category}:")
                    for test_name, test_result in tests.items():
                        status = "✅" if test_result.get('success') else "❌"
                        print(f"     - {test_name}: {status}")
            
            # عرض نتائج الأمان
            if 'security' in result:
                security_results = result['security']
                print("\n🔒 نتائج الأمان:")
                for check_name, check_result in security_results.items():
                    status = "✅" if check_result.get('success') else "❌"
                    print(f"   - {check_name}: {status}")
            
            # عرض نتائج الأداء
            if 'performance' in result:
                performance_results = result['performance']
                print("\n⚡ نتائج الأداء:")
                for opt_name, opt_result in performance_results.items():
                    status = "✅" if opt_result.get('success') else "❌"
                    print(f"   - {opt_name}: {status}")
            
            # عرض التقرير النهائي
            if 'final_report' in result:
                final_report = result['final_report']
                if 'summary' in final_report:
                    summary = final_report['summary']
                    print("\n📈 الملخص النهائي:")
                    print(f"   - إجمالي الاختبارات: {summary.get('total_tests', 0)}")
                    print(f"   - الاختبارات الناجحة: {summary.get('passed_tests', 0)}")
                    print(f"   - معدل النجاح: {summary.get('test_success_rate', 0):.1f}%")
                    print(f"   - درجة الأمان: {summary.get('security_score', 0):.1f}%")
                    print(f"   - درجة الأداء: {summary.get('performance_score', 0):.1f}%")
                    print(f"   - الحالة العامة: {summary.get('overall_status', 'UNKNOWN')}")
            
            # حفظ التقرير
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"PHASE5_FINAL_REPORT_{timestamp}.json"
            
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 تم حفظ التقرير في: {report_filename}")
            
            # إنشاء ملف ملخص
            summary_filename = f"PHASE5_SUMMARY_{timestamp}.md"
            create_summary_file(summary_filename, result)
            print(f"📝 تم إنشاء الملخص في: {summary_filename}")
            
            print("\n🎉 تم إكمال جميع مراحل المشروع بنجاح!")
            print("=" * 60)
            
        else:
            print(f"\n❌ فشل في المرحلة الخامسة: {result.get('error', 'خطأ غير معروف')}")
            
    except Exception as e:
        print(f"\n❌ خطأ في تشغيل المرحلة الخامسة: {str(e)}")
        import traceback
        traceback.print_exc()

def create_summary_file(filename, result):
    """إنشاء ملف ملخص المرحلة الخامسة"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# المرحلة الخامسة: التكامل والاختبار الشامل\n")
            f.write("# Phase 5: Integration and Comprehensive Testing\n\n")
            
            f.write("## 📊 ملخص النتائج\n")
            f.write("### Summary of Results\n\n")
            
            if 'final_report' in result and 'summary' in result['final_report']:
                summary = result['final_report']['summary']
                f.write(f"- **إجمالي الاختبارات:** {summary.get('total_tests', 0)}\n")
                f.write(f"- **الاختبارات الناجحة:** {summary.get('passed_tests', 0)}\n")
                f.write(f"- **معدل النجاح:** {summary.get('test_success_rate', 0):.1f}%\n")
                f.write(f"- **درجة الأمان:** {summary.get('security_score', 0):.1f}%\n")
                f.write(f"- **درجة الأداء:** {summary.get('performance_score', 0):.1f}%\n")
                f.write(f"- **الحالة العامة:** {summary.get('overall_status', 'UNKNOWN')}\n\n")
            
            f.write("## 🔗 المكونات المتكاملة\n")
            f.write("### Integrated Components\n\n")
            
            if 'integration' in result and 'components' in result['integration']:
                components = result['integration']['components']
                for comp_name, comp_result in components.items():
                    status = "✅ نشط" if comp_result.get('success') else "❌ غير نشط"
                    f.write(f"- **{comp_name}:** {status}\n")
            
            f.write("\n## 🧪 نتائج الاختبارات\n")
            f.write("### Test Results\n\n")
            
            if 'testing' in result:
                test_results = result['testing']
                for category, tests in test_results.items():
                    f.write(f"### {category}\n")
                    for test_name, test_result in tests.items():
                        status = "✅" if test_result.get('success') else "❌"
                        f.write(f"- {test_name}: {status}\n")
                    f.write("\n")
            
            f.write("## 🔒 نتائج الأمان\n")
            f.write("### Security Results\n\n")
            
            if 'security' in result:
                security_results = result['security']
                for check_name, check_result in security_results.items():
                    status = "✅" if check_result.get('success') else "❌"
                    f.write(f"- {check_name}: {status}\n")
            
            f.write("\n## ⚡ نتائج الأداء\n")
            f.write("### Performance Results\n\n")
            
            if 'performance' in result:
                performance_results = result['performance']
                for opt_name, opt_result in performance_results.items():
                    status = "✅" if opt_result.get('success') else "❌"
                    f.write(f"- {opt_name}: {status}\n")
            
            f.write("\n## 🎯 الخلاصة\n")
            f.write("### Conclusion\n\n")
            
            if result.get('success'):
                f.write("✅ **تم إكمال المرحلة الخامسة بنجاح!**\n")
                f.write("✅ **Phase 5 completed successfully!**\n\n")
                f.write("تم ربط جميع المكونات واختبار النظام بالكامل.\n")
                f.write("All components have been integrated and the system has been comprehensively tested.\n")
            else:
                f.write("❌ **فشل في المرحلة الخامسة**\n")
                f.write("❌ **Phase 5 failed**\n\n")
                f.write(f"الخطأ: {result.get('error', 'خطأ غير معروف')}\n")
                f.write(f"Error: {result.get('error', 'Unknown error')}\n")
            
    except Exception as e:
        print(f"خطأ في إنشاء ملف الملخص: {str(e)}")

if __name__ == "__main__":
    # تشغيل المرحلة الخامسة
    asyncio.run(main())