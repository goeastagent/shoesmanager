#!/usr/bin/env python3
"""
윈도우 실행파일 빌드 스크립트

PyInstaller를 사용하여 GUI 애플리케이션을 윈도우 실행파일(.exe)로 빌드합니다.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """PyInstaller 설치 확인 및 설치"""
    try:
        import PyInstaller
        print("✅ PyInstaller가 이미 설치되어 있습니다.")
        return True
    except ImportError:
        print("❌ PyInstaller가 설치되어 있지 않습니다.")
        print("📦 PyInstaller를 설치합니다...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller 설치 완료!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ PyInstaller 설치 실패: {e}")
            return False

def create_spec_file():
    """PyInstaller spec 파일 생성"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/ui/tk_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app/config.py', 'app'),
        ('app/models.py', 'app'),
        ('app/schemas.py', 'app'),
        ('app/repository.py', 'app'),
        ('app/db.py', 'app'),
        ('app/utils.py', 'app'),
        ('app/services', 'app/services'),
        ('app/migrations', 'app/migrations'),
        ('inventory_management.db', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'sqlalchemy',
        'sqlalchemy.orm',
        'sqlalchemy.ext.declarative',
        'pydantic',
        'pydantic_settings',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'decimal',
        'datetime',
        'uuid',
        'threading',
        'logging',
        'csv',
        'json',
        'pathlib',
        'typing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ShoesManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 애플리케이션이므로 콘솔 창 숨김
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 아이콘 파일이 있다면 여기에 경로 지정
)
'''
    
    with open('ShoesManager.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ ShoesManager.spec 파일이 생성되었습니다.")

def build_executable():
    """실행파일 빌드"""
    print("🔨 실행파일 빌드를 시작합니다...")
    
    try:
        # PyInstaller로 빌드 실행
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "ShoesManager.spec"
        ])
        
        print("✅ 빌드가 완료되었습니다!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 빌드 실패: {e}")
        return False

def create_distribution():
    """배포용 폴더 생성"""
    print("📦 배포용 폴더를 생성합니다...")
    
    dist_dir = Path("dist/ShoesManager")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # 실행파일 복사
    exe_file = Path("dist/ShoesManager.exe")
    if exe_file.exists():
        shutil.copy2(exe_file, dist_dir.parent / "ShoesManager.exe")
        print("✅ 실행파일이 dist 폴더에 복사되었습니다.")
    
    # README 파일 생성
    readme_content = """# 신발 관리 시스템 (ShoesManager)

## 실행 방법
1. ShoesManager.exe 파일을 더블클릭하여 실행합니다.
2. 프로그램이 시작되면 재고 관리 화면이 표시됩니다.

## 주요 기능
- 재고 항목 추가/수정/삭제
- 바코드 스캔을 통한 자동 정보 입력
- 바코드로 판매 처리
- CSV 가져오기/내보내기
- HTML 보고서 생성

## 시스템 요구사항
- Windows 10 이상
- .NET Framework 4.7.2 이상 (필요시)

## 문제 해결
- 프로그램이 실행되지 않으면 관리자 권한으로 실행해보세요.
- 바이러스 백신 프로그램에서 차단하는 경우 예외 처리해주세요.

## 지원
문제가 발생하면 개발자에게 문의하세요.
"""
    
    with open("dist/README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ README.txt 파일이 생성되었습니다.")

def main():
    """메인 함수"""
    print("🚀 윈도우 실행파일 빌드를 시작합니다...")
    print("=" * 50)
    
    # 현재 디렉토리 확인
    if not Path("app/ui/tk_app.py").exists():
        print("❌ 프로젝트 루트 디렉토리에서 실행해주세요.")
        return False
    
    # PyInstaller 확인 및 설치
    if not check_pyinstaller():
        return False
    
    # spec 파일 생성
    create_spec_file()
    
    # 실행파일 빌드
    if not build_executable():
        return False
    
    # 배포용 폴더 생성
    create_distribution()
    
    print("=" * 50)
    print("🎉 빌드가 성공적으로 완료되었습니다!")
    print("📁 실행파일 위치: dist/ShoesManager.exe")
    print("📄 README 파일: dist/README.txt")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
