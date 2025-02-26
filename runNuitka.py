import os

os.system(
    f"python3 -m nuitka  "
    f'--product-name="Back SEO Agencies"  '
    f"--file-version=1.0.0.0  "
    f"--product-version=1.0.0.0  "
    f'--file-description="Back SEO Agency App"  '
    f'--copyright="© Andrew Cook. All rights reserved."  '
    f'--trademarks="Dont be dumb, talk to me about white labeling"  '
    f'--report="somereport.rst"  '
    f"--report-template=LicenseReport.rst.j2:LicenseReport.rst  "
#    f"--clang  "
    f"--output-dir=nuitkastyle  "
    f"--include-data-files=Utils/certifi/cacert.pem=Utils/certifi/cacert.pem  "
    f"--include-data-files=chromium1084/**/*.dll=chromium-1084/chrome-win/  "
    f"--include-data-files=themes/*.ini=themes/  "
    f"--include-data-dir=chromium1084=chromium-1084  "
    f"--include-data-dir=SEO/Resources/templates=SEO/Resources/templates  "
    f"--include-data-dir=images=./  "
    f"--include-plugin-directory=Plugins  "
    f"--include-data-dir=Plugins=Plugins  "
    f"--include-package-data=playwright  "
    f"--include-package-data=playwright.async_api  "
    f"--include-package-data=geopy  "
    f"--include-package-data=docxtpl  "
    f"--include-package-data=docxcompose  "
    f"--include-package-data=docx  "
    f"--include-package=playwright "
    f"--include-package=playwright.async_api "
    f"--include-package=geopy  "
    f"--assume-yes-for-downloads  "
    f"--disable-console  "
    f"--standalone main.py"
)
