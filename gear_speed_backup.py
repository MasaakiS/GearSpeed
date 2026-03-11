import math
import ui
import console
import dialogs
import json
import os
import clipboard
import re
import locale

# 言語検出と多言語対応
def get_system_language():
    """システム言語を検出"""
    try:
        # Pythonistaでの言語検出
        from objc_util import ObjCClass
        NSLocale = ObjCClass('NSLocale')
        
        # preferredLanguagesの最初の言語を優先
        try:
            preferred = NSLocale.preferredLanguages()
            if preferred and len(preferred) > 0:
                first_lang = str(preferred[0])
                if first_lang.startswith('ja'):
                    return 'ja'
        except:
            pass
        
        # フォールバック: currentLocaleのlanguageCode
        current_locale = NSLocale.currentLocale()
        lang_code = str(current_locale.languageCode())
        return lang_code
            
    except:
        # フォールバック: localeモジュールを使用
        try:
            lang = locale.getdefaultlocale()[0]
            if lang and lang.startswith('ja'):
                return 'ja'
        except:
            pass
    return 'en'

# 言語設定
LANG = get_system_language()
IS_JAPANESE = LANG == 'ja'

# ダークモード検出
def is_dark_mode():
    """システムのダークモード設定を検出"""
    try:
        from objc_util import ObjCClass
        
        # 方法1: UITraitCollectionを直接使用
        try:
            UITraitCollection = ObjCClass('UITraitCollection')
            current_trait = UITraitCollection.currentTraitCollection()
            style = current_trait.userInterfaceStyle()
            # 0 = unspecified, 1 = light, 2 = dark
            if style == 2:
                return True
        except:
            pass
        
        # 方法2: UIScreenのtraitCollectionを使用
        try:
            UIScreen = ObjCClass('UIScreen')
            screen = UIScreen.mainScreen()
            trait_collection = screen.traitCollection()
            style = trait_collection.userInterfaceStyle()
            if style == 2:
                return True
        except:
            pass
        
        # 方法3: キーウィンドウのtraitCollectionを使用
        try:
            UIApplication = ObjCClass('UIApplication')
            app = UIApplication.sharedApplication()
            # iOS 13以降のシーンベースのウィンドウ取得
            try:
                scenes = app.connectedScenes()
                for scene in scenes:
                    if scene.activationState() == 0:  # foregroundActive
                        windows = scene.windows()
                        if windows and len(windows) > 0:
                            window = windows[0]
                            trait = window.traitCollection()
                            if trait.userInterfaceStyle() == 2:
                                return True
            except:
                pass
            
            # 従来のウィンドウ取得方法
            try:
                key_window = app.keyWindow()
                if key_window:
                    trait = key_window.traitCollection()
                    if trait.userInterfaceStyle() == 2:
                        return True
            except:
                pass
        except:
            pass
        
        return False
    except Exception as e:
        print(f'ダークモード検出エラー: {e}')
        return False

# 設定ファイルのパスを取得
def get_settings_file_path():
    """設定ファイルのパスを取得（Pythonista 3対応）"""
    try:
        # __file__が使える場合
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bike_speed_settings.json')
    except NameError:
        # Pythonista 3では__file__が使えない場合がある
        # カレントディレクトリを使用
        import sys
        if hasattr(sys, 'argv') and sys.argv and sys.argv[0]:
            script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            if script_dir:
                return os.path.join(script_dir, 'bike_speed_settings.json')
        # フォールバック: ドキュメントディレクトリ
        return os.path.expanduser('~/Documents/bike_speed_settings.json')

SETTINGS_FILE_PATH = get_settings_file_path()

# テーマ設定を読み込む
def get_theme_setting():
    """設定ファイルからテーマ設定を読み込む"""
    try:
        if os.path.exists(SETTINGS_FILE_PATH):
            with open(SETTINGS_FILE_PATH, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings.get('theme', 'auto')  # 'auto', 'light', 'dark'
    except:
        pass
    return 'auto'

def determine_dark_mode():
    """テーマ設定に基づいてダークモードかどうかを決定"""
    theme_setting = get_theme_setting()
    if theme_setting == 'dark':
        return True
    elif theme_setting == 'light':
        return False
    else:  # auto
        return is_dark_mode()

IS_DARK_MODE = determine_dark_mode()
print(f'ダークモード: {IS_DARK_MODE} (設定: {get_theme_setting()})')  # デバッグ用

# テーマカラー定義
class Theme:
    """ライト/ダークモード対応のテーマカラー"""
    
    @staticmethod
    def get_colors():
        if IS_DARK_MODE:
            return {
                # 背景色（より深い黒でコントラスト向上）
                'bg_primary': '#000000',      # メイン背景（純黒）
                'bg_secondary': '#1c1c1e',    # セカンダリ背景
                'bg_tertiary': '#2c2c2e',     # カード・入力エリア背景
                'bg_elevated': '#3a3a3c',     # 浮き上がった要素
                'bg_card': '#1c1c1e',         # カード背景
                
                # テキスト色
                'text_primary': '#ffffff',    # メインテキスト
                'text_secondary': '#ebebf5',  # セカンダリテキスト
                'text_tertiary': '#8e8e93',   # 補助テキスト
                
                # ボーダー色（控えめに）
                'border': '#38383a',
                'border_light': '#2c2c2e',
                
                # アクセントカラー（より鮮やかに）
                'accent_blue': '#0a84ff',
                'accent_green': '#32d74b',
                'accent_orange': '#ff9f0a',
                'accent_red': '#ff453a',
                'accent_purple': '#bf5af2',
                'accent_gray': '#48484a',
                
                # テーブル色
                'table_header': '#1c1c1e',
                'table_header_text': '#ffffff',
                'table_row_odd': '#000000',
                'table_row_even': '#1c1c1e',
                'table_cell_bg': '#1c1c1e',
                'table_cell_highlight': '#2c2c2e',
                'table_number_bg': '#0a84ff',
                'table_gear_bg': '#2c2c2e',
                
                # ボタン色（グラデーション風）
                'btn_primary': '#0a84ff',
                'btn_primary_pressed': '#0066cc',
                'btn_danger': '#ff453a',
                'btn_success': '#32d74b',
                'btn_warning': '#ff9f0a',
                'btn_secondary': '#48484a',
                
                # セグメントコントロール
                'segment_bg': '#1c1c1e',
                'segment_selected': '#48484a',
                
                # ギア選択エリア
                'gear_scroll_bg': '#1c1c1e',
                'gear_btn_normal': '#2c2c2e',
                'gear_btn_selected': '#0a84ff',
                'gear_btn_text': '#ffffff',
            }
        else:
            return {
                # 背景色（よりクリーンな白）
                'bg_primary': '#f2f2f7',      # メイン背景（iOS標準）
                'bg_secondary': '#ffffff',    # セカンダリ背景
                'bg_tertiary': '#ffffff',     # カード・入力エリア背景
                'bg_elevated': '#ffffff',     # 浮き上がった要素
                'bg_card': '#ffffff',         # カード背景
                
                # テキスト色
                'text_primary': '#000000',    # メインテキスト
                'text_secondary': '#3c3c43',  # セカンダリテキスト
                'text_tertiary': '#8e8e93',   # 補助テキスト
                
                # ボーダー色（控えめに）
                'border': '#c6c6c8',
                'border_light': '#e5e5ea',
                
                # アクセントカラー（iOS標準）
                'accent_blue': '#007aff',
                'accent_green': '#34c759',
                'accent_orange': '#ff9500',
                'accent_red': '#ff3b30',
                'accent_purple': '#af52de',
                'accent_gray': '#8e8e93',
                
                # テーブル色
                'table_header': '#007aff',
                'table_header_text': '#ffffff',
                'table_row_odd': '#ffffff',
                'table_row_even': '#f9f9f9',
                'table_cell_bg': '#f9f9f9',
                'table_cell_highlight': '#f2f2f7',
                'table_number_bg': '#007aff',
                'table_gear_bg': '#f2f2f7',
                
                # ボタン色
                'btn_primary': '#007aff',
                'btn_primary_pressed': '#0056b3',
                'btn_danger': '#ff3b30',
                'btn_success': '#34c759',
                'btn_warning': '#ff9500',
                'btn_secondary': '#8e8e93',
                
                # セグメントコントロール
                'segment_bg': '#e5e5ea',
                'segment_selected': '#ffffff',
                
                # ギア選択エリア
                'gear_scroll_bg': '#f2f2f7',
                'gear_btn_normal': '#ffffff',
                'gear_btn_selected': '#007aff',
                'gear_btn_text': '#000000',
            }

# グローバルテーマ色を取得
COLORS = Theme.get_colors()

# 多言語文字列辞書
STRINGS = {
    # UI Labels
    'front_gear_label': ('Front Gear:', 'フロントギア:'),
    'wheel_label': ('Wheel:', 'ホイール:'),
    'tire_width_label': ('Tire Width:', 'タイヤ幅:'),
    'mode_label': ('Mode:', 'モード:'),
    'generate_btn': ('Generate', '速度表生成'),
    'clear_btn': ('Clear', 'クリア'),
    'save_btn': ('💾Save', '💾保存'),
    'load_btn': ('📂Load', '📂読込'),
    'delete_btn': ('🗑Del', '🗑削除'),
    'paste_btn': ('📋Paste', '📋ペースト'),
    'mode_all': ('All', '全表示'),
    'mode_custom': ('Custom', 'カスタム'),
    'selected_count': ('Sel: {0}', '選択: {0}枚'),
    'placeholder': ('Enter number', '数字を入力'),
    
    # Welcome message
    'welcome_message': ('🚴 GearSpeed\n\nPress "Generate" to start\n\nTap [?] for help', 
                       '🚴 GearSpeed\n\n「速度表生成」ボタンを押して開始\n\n使い方は [?] ボタンで確認できます'),
    
    # Help dialog
    'help_title': ('🚴 GearSpeed Help', '🚴 GearSpeed ヘルプ'),
    'help_text': ('''📋 How to use:
1. Select front gear, wheel size and tire width
2. Press "Generate" button

📊 Supported range:
・Front: 20-60T / Rear: 9-51T
・Wheel: 700c (ETRTO 622mm) / 650c (ETRTO 571mm)
・Tire Width: 23-50mm
・Outer diameter = Rim diameter + 2 × Tire width + 5mm
・Cadence: 70-110 rpm

🔧 Display modes:
・All: Show all 9-51T gears
・Custom: Select freely from 9-51T

💾 Preset feature:
・Manage with Save/Load/Delete buttons

📋 Paste:
Bulk set from gear config text

💡 Tap row for details
📊 Legend button for table guide''',
'''📋 使い方:
1. フロントギア、ホイールサイズ、タイヤ幅を選択
2. 「速度表生成」ボタンを押す

📊 対応範囲:
・Front: 20-60T / Rear: 9-51T
・Wheel: 700c (ETRTO 622mm) / 650c (ETRTO 571mm)
・タイヤ幅: 23-50mm
・外径 = リム径 + 2 × タイヤ幅 + 5mm
・Cadence: 70-110 rpm

🔧 表示モード:
・全表示: 9-51Tの全歯数を表示
・カスタム: 9-51Tから自由に選択

💾 プリセット機能:
・保存/読込/削除ボタンで管理

📋 ペースト:
ギア構成テキストから一括設定

💡 行タップで詳細表示
📊 凡例ボタンで表の見方を確認'''),
    
    # Legend dialog
    'legend_title': ('📊 Table Legend', '📊 表の凡例'),
    'legend_text': ('''📊 How to read the table:

【Column descriptions】
# : Row number
T : Rear gear teeth
Ratio : Gear ratio (Front÷Rear)
ΔR : Ratio diff to next gear
70-110 : Speed at each cadence (km/h)

【Speed color coding】
🔵 Blue: Low speed (0-15km/h)
🟢 Green: Medium speed (15-30km/h)
🟡 Yellow: High speed (30-45km/h)
🔴 Red: Very high speed (45km/h+)

【ΔR (ratio diff) color coding】
🟢 Green: Ideal (0.05-0.15)
🟡 Yellow: Standard (0.15-0.30)
🔴 Red: Wide gap (0.30+)

💡 Tap a row for usage details''',
'''📊 表の見方:

【列の説明】
# : 行番号
T : リアギア歯数
Ratio : ギア比 (Front÷Rear)
ΔR : 次段とのギア比差
70-110 : 各ケイデンスでの速度(km/h)

【速度の色分け】
🔵 青系: 低速域 (0-15km/h)
🟢 緑系: 中速域 (15-30km/h)
🟡 黄系: 高速域 (30-45km/h)
🔴 赤系: 超高速域 (45km/h以上)

【ΔR（ギア比差）の色分け】
🟢 緑系: 理想的 (0.05-0.15)
🟡 黄系: 標準的 (0.15-0.30)
🔴 赤系: 間隔広い (0.30以上)

💡 行をタップすると用途の詳細を表示'''),
    
    # Gear usage descriptions
    'usage_sprint': ('⚡ Ultra high - Sprint/Downhill', '⚡ 超高速域 - スプリント・下り坂専用'),
    'usage_race': ('🏁 High speed - Race/Fast cruise', '🏁 高速域 - レース・高速巡航'),
    'usage_normal': ('🚴‍♂️ Normal - General cruising', '🚴‍♂️ 標準域 - 一般的な巡航速度'),
    'usage_climb': ('🏔️ Climbing - Hills/Headwind', '🏔️ 登坂域 - 坂道・向かい風対応'),
    'usage_steep': ('⛰️ Steep climb - Steep hills', '⛰️ 激坂域 - 急坂・激坂専用'),
    'detail_msg': ('{0}T: {1}\nRatio {2:.2f}, 90rpm={3:.1f}km/h', '{0}T: {1}\n比率{2:.2f}, 90rpm={3:.1f}km/h'),
    
    # Error messages
    'err_front_range': ('Front gear must be 20-60', 'フロントギアは20-60の範囲で入力してください'),
    'err_custom_select': ('Select gears for custom mode', 'カスタムモードでは歯数を選択してください'),
    'err_invalid_number': ('Enter a valid number', '有効な数値を入力してください'),
    'err_clipboard_empty': ('Clipboard is empty', 'クリップボードが空です'),
    'err_no_gears_found': ('No gear config found\nCopy numbers', 'ギア構成が見つかりませんでした\n数字をコピーしてください'),
    'err_error': ('Error: {0}', 'エラー: {0}'),
    'err_select_gears_to_save': ('Select gears to save', '保存するギアを選択してください'),
    'err_save_failed': ('Save failed', '保存に失敗しました'),
    'err_enter_name': ('Enter a name', '名前を入力してください'),
    'err_no_presets': ('No saved presets', '保存されたプリセットがありません'),
    'err_no_presets_to_delete': ('No presets to delete', '削除するプリセットがありません'),
    'err_delete_failed': ('Delete failed', '削除に失敗しました'),
    'err_enter_number': ('Enter a number', '数字を入力してください'),
    
    # Preset messages
    'preset_save_title': ('Save Preset', 'プリセット保存'),
    'preset_save_prompt': ('Save current config ({0} gears) with a name', '現在の設定 ({0}枚) に名前を付けて保存します'),
    'preset_saved': ('"{0}" saved\n{1}', '「{0}」を保存しました\n{1}'),
    'preset_load_title': ('Load Preset', 'プリセット読込'),
    'preset_load_prompt': ('Enter number:\n\n{0}', '番号を入力してください:\n\n{0}'),
    'preset_loaded': ('"{0}" loaded', '「{0}」を読み込みました'),
    'preset_delete_title': ('Delete Preset', 'プリセット削除'),
    'preset_delete_prompt': ('Enter number to delete:\n\n{0}', '削除する番号を入力:\n\n{0}'),
    'preset_delete_confirm_title': ('Confirm Delete', '削除確認'),
    'preset_delete_confirm': ('Delete "{0}"?', '「{0}」を削除しますか？'),
    'preset_deleted': ('"{0}" deleted', '「{0}」を削除しました'),
    
    # Paste result
    'paste_result': ('{0} gears set\n{1}', '{0}枚のギアを設定\n{1}'),
    
    # Share feature
    'share_btn': ('📤', '📤'),
    'share_title': ('GearSpeed - Speed Table', 'GearSpeed 速度表'),
    'share_no_data': ('Generate table first', '先に速度表を生成してください'),
    'share_success': ('Ready to share', '共有の準備ができました'),
    'share_clipboard': ('Copied to clipboard', 'クリップボードにコピーしました'),
    
    # Theme settings
    'theme_title': ('Theme', 'テーマ'),
    'theme_auto': ('Auto (System)', '自動（システム設定）'),
    'theme_light': ('Light', 'ライト'),
    'theme_dark': ('Dark', 'ダーク'),
    'theme_changed': ('Theme changed. Restart app.', 'テーマを変更しました。アプリを再起動してください。'),
}

def _(key, *args):
    """多言語文字列を取得"""
    if key in STRINGS:
        text = STRINGS[key][1] if IS_JAPANESE else STRINGS[key][0]
        if args:
            return text.format(*args)
        return text
    return key

class CustomSpeedTable:
    """ScrollViewベースのカスタム表"""
    def __init__(self, container_view):
        self.container_view = container_view
        self.data = []
        self.header_view = None
        self.scroll_view = None
        self.content_view = None
        self.row_views = []
        
        # 列幅設定
        self.column_widths = [25, 35, 50, 45, 40, 40, 40, 40, 40]  # #, T, Ratio, ΔR, 70, 80, 90, 100, 110
        self.row_height = 35
        self.header_height = 40
        
    def setup_table(self):
        """表の基本構造をセットアップ"""
        # メインコンテナをクリア
        for subview in list(self.container_view.subviews):
            self.container_view.remove_subview(subview)
            
        # ヘッダービュー作成
        self.header_view = ui.View()
        self.header_view.background_color = COLORS['table_header']
        self.header_view.corner_radius = 12
        self.header_view.frame = (0, 0, self.container_view.width, self.header_height)
        self.header_view.flex = 'W'
        self.container_view.add_subview(self.header_view)
        
        # ScrollView作成
        self.scroll_view = ui.ScrollView()
        self.scroll_view.frame = (0, self.header_height, self.container_view.width, 
                                 self.container_view.height - self.header_height)
        self.scroll_view.flex = 'WH'
        self.scroll_view.shows_horizontal_scroll_indicator = False
        self.scroll_view.shows_vertical_scroll_indicator = True
        self.scroll_view.always_bounce_vertical = True
        self.scroll_view.background_color = COLORS['bg_card']
        self.scroll_view.bounces = True
        self.container_view.add_subview(self.scroll_view)
        
        # コンテンツビュー作成
        self.content_view = ui.View()
        self.content_view.frame = (0, 0, sum(self.column_widths), 0)  # 高さは動的設定
        self.scroll_view.add_subview(self.content_view)
        
        # ヘッダー作成
        self.create_header()
        
    def create_header(self):
        """ヘッダー行を作成"""
        # 画面幅に応じてヘッダーを調整
        is_landscape = self.container_view.width > 400
        
        # 9列表示（番号列と差分列を追加）
        headers = ['#', 'T', 'Ratio', 'ΔR', '70', '80', '90', '100', '110']
        if not is_landscape:
            # 縦画面では列幅を狭く調整
            self.column_widths = [22, 30, 45, 40, 35, 35, 35, 35, 35]
            
        x = 0
        for i, (header, width) in enumerate(zip(headers, self.column_widths)):
            label = ui.Label()
            label.text = header
            label.font = ('<system-bold>', 13)
            label.text_color = COLORS['table_header_text']
            label.alignment = ui.ALIGN_CENTER
            label.background_color = COLORS['table_header']
            label.border_width = 0
            label.border_color = COLORS['border_light']
            label.frame = (x, 0, width, self.header_height)
            self.header_view.add_subview(label)
            x += width
            
    def update_data(self, data):
        """データを更新して表を再描画"""
        self.data = data
        self.clear_rows()
        self.create_rows()
        
    def clear_rows(self):
        """既存の行をクリア"""
        for row_view in self.row_views:
            if row_view.superview:
                row_view.superview.remove_subview(row_view)
        self.row_views = []
        
    def create_rows(self):
        """データ行を作成"""
        is_landscape = self.container_view.width > 400
        
        for row_index, row_data in enumerate(self.data):
            row_view = self.create_row(row_data, row_index, is_landscape)
            self.content_view.add_subview(row_view)
            self.row_views.append(row_view)
            
        # コンテンツサイズを更新（下部に余白を追加）
        content_height = len(self.data) * self.row_height
        bottom_padding = 40  # iPhoneの画面下部の角の丸みに対応する余白
        self.content_view.frame = (0, 0, sum(self.column_widths), content_height + bottom_padding)
        self.scroll_view.content_size = (sum(self.column_widths), content_height + bottom_padding)
        
    def create_row(self, row_data, row_index, is_landscape):
        """単一行を作成"""
        row_view = ui.View()
        y_pos = row_index * self.row_height
        row_view.frame = (0, y_pos, sum(self.column_widths), self.row_height)
        
        # 背景色はテーマに応じて設定（セル単位で色分けするため）
        row_view.background_color = COLORS['bg_card']
            
        # セル作成（9列表示：番号列と差分列を追加）
        ratio_diff = row_data.get('ratio_diff', '')
        ratio_diff_str = f"{ratio_diff:.2f}" if ratio_diff else '-'
        
        values = [
            str(row_index + 1),  # 番号（1から開始）
            str(row_data['rear']),
            f"{row_data['gear_ratio']:.2f}",
            ratio_diff_str,
            f"{row_data['70rpm']:.1f}",
            f"{row_data['80rpm']:.1f}", 
            f"{row_data['90rpm']:.1f}",
            f"{row_data['100rpm']:.1f}",
            f"{row_data['110rpm']:.1f}"
        ]
        speeds = [None, None, None, None, row_data['70rpm'], row_data['80rpm'], 
                 row_data['90rpm'], row_data['100rpm'], row_data['110rpm']]
            
        x = 0
        for i, (value, width) in enumerate(zip(values, self.column_widths)):
            speed = speeds[i] if i < len(speeds) else None
            # ΔR列（インデックス3）の場合は差分値を渡す
            ratio_diff_value = row_data.get('ratio_diff', None) if i == 3 else None
            # 番号列（インデックス0）は特別なスタイル
            is_number_column = (i == 0)
            is_gear_column = (i == 1)
            cell = self.create_cell(value, x, 0, width, self.row_height, is_gear_column, speed, ratio_diff_value, is_number_column)
            row_view.add_subview(cell)
            x += width
            
        # タップ処理
        def handle_tap(sender):
            self.show_detail_info(row_data)
        row_view.action = handle_tap
        row_view.touch_enabled = True
            
        return row_view
        
    def create_cell(self, text, x, y, width, height, is_gear_column=False, speed=None, ratio_diff=None, is_number_column=False):
        """個別セルを作成"""
        label = ui.Label()
        label.text = text
        label.font = ('<system>', 12)
        label.text_color = COLORS['text_primary']
        label.alignment = ui.ALIGN_CENTER
        label.frame = (x, y, width, height)
        label.border_width = 0
        label.border_color = COLORS['border_light']
        
        # 番号列は特別なスタイル
        if is_number_column:
            label.font = ('<system-bold>', 11)
            label.text_color = 'white'
            label.background_color = COLORS['table_number_bg']
        # 速度に基づく色分け（速度セルのみ）
        elif speed is not None:
            label.background_color = self.get_speed_color(speed)
            # 高速域では白文字、低速域では黒文字
            if speed > 45:
                label.text_color = 'white'
            else:
                label.text_color = '#333333'
        # △R列の色分け
        elif ratio_diff is not None:
            label.background_color = self.get_ratio_diff_color(ratio_diff)
            label.text_color = '#333333'
        else:
            label.background_color = COLORS['table_cell_bg']
        
        # ギア列は太字
        if is_gear_column:
            label.font = ('<system-bold>', 12)
            label.text_color = COLORS['text_secondary']
            label.background_color = COLORS['table_gear_bg']
            
        return label
    
    def get_speed_color(self, speed):
        """速度に基づく色を計算（青→緑→黄→赤のグラデーション）"""
        # 速度範囲を0-60km/hと仮定してグラデーション計算
        speed = max(0, min(speed, 60))  # 0-60の範囲に制限
        ratio = speed / 60.0
        
        if ratio <= 0.25:  # 0-15km/h: 青系
            # 濃い青 → 青
            r = int(52 + (100 - 52) * (ratio / 0.25))
            g = int(152 + (180 - 152) * (ratio / 0.25))  
            b = int(219 + (255 - 219) * (ratio / 0.25))
        elif ratio <= 0.5:  # 15-30km/h: 青 → 緑
            # 青 → 緑
            local_ratio = (ratio - 0.25) / 0.25
            r = int(100 + (76 - 100) * local_ratio)
            g = int(180 + (205 - 180) * local_ratio)
            b = int(255 + (92 - 255) * local_ratio)
        elif ratio <= 0.75:  # 30-45km/h: 緑 → 黄
            # 緑 → 黄
            local_ratio = (ratio - 0.5) / 0.25
            r = int(76 + (255 - 76) * local_ratio)
            g = int(205 + (235 - 205) * local_ratio)
            b = int(92 + (59 - 92) * local_ratio)
        else:  # 45-60km/h: 黄 → 赤
            # 黄 → 赤  
            local_ratio = (ratio - 0.75) / 0.25
            r = int(255)
            g = int(235 + (99 - 235) * local_ratio)
            b = int(59 + (71 - 59) * local_ratio)
        
        # RGB値を16進数に変換
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def get_ratio_diff_color(self, ratio_diff):
        """ギア比の差に基づく色を計算（緑→黄→赤のグラデーション）"""
        # 差が小さい（0.05-0.15）: 緑系（理想的）
        # 差が中程度（0.15-0.30）: 黄色系（標準的）
        # 差が大きい（0.30以上）: 赤系（ギア間隔が広い）
        
        ratio_diff = abs(ratio_diff)  # 絶対値を使用
        ratio_diff = max(0.05, min(ratio_diff, 0.50))  # 0.05-0.50の範囲に制限
        
        if ratio_diff <= 0.15:  # 理想的な範囲: 緑系
            # 濃い緑 → 緑
            local_ratio = (ratio_diff - 0.05) / 0.10
            r = int(76 - (76 - 46) * local_ratio)
            g = int(175 + (205 - 175) * local_ratio)
            b = int(80 - (80 - 92) * local_ratio)
        elif ratio_diff <= 0.30:  # 標準的な範囲: 緑 → 黄
            local_ratio = (ratio_diff - 0.15) / 0.15
            r = int(46 + (255 - 46) * local_ratio)
            g = int(205 + (235 - 205) * local_ratio)
            b = int(92 - (92 - 59) * local_ratio)
        else:  # 広い範囲: 黄 → 赤
            local_ratio = min((ratio_diff - 0.30) / 0.20, 1.0)
            r = int(255)
            g = int(235 - (235 - 140) * local_ratio)
            b = int(59 - (59 - 50) * local_ratio)
        
        return f'#{r:02x}{g:02x}{b:02x}'
        
    def show_detail_info(self, row_data):
        """詳細情報を表示"""
        rear_gear = row_data['rear']
        
        # 用途判定
        if rear_gear <= 12:
            usage = _('usage_sprint')
        elif rear_gear <= 15:
            usage = _('usage_race')
        elif rear_gear <= 20:
            usage = _('usage_normal')
        elif rear_gear <= 28:
            usage = _('usage_climb')
        else:
            usage = _('usage_steep')
            
        detail_msg = _('detail_msg', rear_gear, usage, row_data['gear_ratio'], row_data['90rpm'])
        console.hud_alert(detail_msg, 'success', 3)
        
    def update_layout(self, new_width, new_height):
        """レイアウトを更新"""
        is_landscape = new_width > 400
        
        # 列幅を調整（縦横共に9列表示）
        if is_landscape:
            self.column_widths = [30, 40, 60, 50, 50, 50, 50, 50, 50]  # #, R, Ratio, ΔR, 70, 80, 90, 100, 110
        else:
            self.column_widths = [22, 35, 50, 40, 40, 40, 40, 40, 40]  # 縦画面用狭い列幅
            
        # ヘッダーとScrollViewのサイズ更新
        if self.header_view:
            self.header_view.frame = (0, 0, new_width, self.header_height)
        if self.scroll_view:
            self.scroll_view.frame = (0, self.header_height, new_width, new_height - self.header_height)
        
        # データがある場合は再描画
        if self.data:
            self.setup_table()
            self.update_data(self.data)

class BikeSpeedCalculator:
    def __init__(self):
        # ETRTO規格のリム径（mm）
        self.rim_diameter = 622  # デフォルトは700c（ETRTO 622mm）
        self.tire_width = 28  # デフォルトタイヤ幅（mm）
        
    def set_wheel_size(self, wheel_size):
        """ホイールサイズを設定（ETRTO規格のリム径）"""
        if wheel_size == "700c":
            self.rim_diameter = 622  # ETRTO 622mm
        elif wheel_size == "650c":
            self.rim_diameter = 571  # ETRTO 571mm
        else:
            raise ValueError("対応していないホイールサイズです")
    
    def set_tire_width(self, width_mm):
        """タイヤ幅を設定（mm）"""
        if 20 <= width_mm <= 50:
            self.tire_width = width_mm
        else:
            raise ValueError("タイヤ幅は20-50mmの範囲で指定してください")
    
    def get_wheel_diameter(self):
        """タイヤの外径を計算（リム径 + 2 × タイヤ幅 + 5mm）
        +5mmは荷重によるタイヤの縦方向への膨らみを考慮"""
        return self.rim_diameter + 2 * self.tire_width + 5
        
    def calculate_speed(self, front_gear, rear_gear, cadence_rpm):
        """ロードバイクの速度を計算する"""
        gear_ratio = front_gear / rear_gear
        wheel_diameter = self.get_wheel_diameter()
        wheel_circumference_mm = math.pi * wheel_diameter
        distance_per_minute_mm = cadence_rpm * gear_ratio * wheel_circumference_mm
        speed_kmh = (distance_per_minute_mm * 60) / (1000 * 1000)
        return round(speed_kmh, 1)
    
    def create_speed_table(self, front_gear, rear_gears=None):
        """指定されたフロントギアの速度表を作成"""
        if rear_gears is None:
            rear_gears = list(range(9, 52))  # 9T-51T 全範囲対応
        cadence_values = [70, 80, 90, 100, 110]
        
        results = []
        for i, rear in enumerate(rear_gears):
            row = {'rear': rear, 'gear_ratio': round(front_gear/rear, 2)}
            for cadence in cadence_values:
                speed = self.calculate_speed(front_gear, rear, cadence)
                row[f'{cadence}rpm'] = speed
            
            # 次のギア（より大きい歯数）との比率の差を計算
            if i < len(rear_gears) - 1:
                next_ratio = front_gear / rear_gears[i + 1]
                row['ratio_diff'] = round(row['gear_ratio'] - next_ratio, 2)
            else:
                row['ratio_diff'] = None
            
            results.append(row)
        
        return results

class MainView(ui.View):
    """メインビュー（レイアウト処理用）"""
    def __init__(self, app):
        super().__init__()
        self.app = app
    
    def layout(self):
        """ビューのサイズが変更されたときに呼ばれる"""
        if self.app:
            self.app.layout_subviews()

class BikeSpeedApp:
    # 設定ファイルパス（グローバル変数を使用）
    SETTINGS_FILE = SETTINGS_FILE_PATH
    
    def __init__(self):
        self.calculator = BikeSpeedCalculator()
        self.custom_table = None
        self.selected_gears = set()  # 選択された歯数を管理
        self.gear_buttons = {}  # 歯数ボタンの辞書
        self.welcome_label = None  # 初期化
        # 共有用データ
        self.current_table_data = None
        self.current_front_gear = None
        self.current_wheel_size = None
        self.current_tire_width = None
        self.tire_width_value = 28  # デフォルトタイヤ幅（mm）
        self.setup_ui()
        self.load_settings()  # 前回の設定を読み込み
    
    def save_settings(self):
        """現在の設定を保存"""
        # 既存のプリセットを読み込み
        existing_presets = {}
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    old_settings = json.load(f)
                    existing_presets = old_settings.get('named_presets', {})
        except:
            pass
        
        settings = {
            'front_gear': self.front_gear_value,
            'wheel_size': self.wheel_segment.selected_index,
            'tire_width': self.tire_width_value,
            'display_mode': self.mode_segment.selected_index,
            'selected_gears': list(self.selected_gears),
            'named_presets': existing_presets
        }
        try:
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f'設定の保存に失敗: {e}')
    
    def load_settings(self):
        """保存された設定を読み込み"""
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # フロントギアを復元
                if 'front_gear' in settings:
                    try:
                        value = int(settings['front_gear'])
                        if 20 <= value <= 60:
                            self.front_gear_value = value
                            self.front_btn.title = f'{value}T ▼'
                    except:
                        pass
                
                # ホイールサイズを復元
                if 'wheel_size' in settings:
                    self.wheel_segment.selected_index = settings['wheel_size']
                    wheel_sizes = ['700c', '650c']
                    self.calculator.set_wheel_size(wheel_sizes[settings['wheel_size']])
                
                # タイヤ幅を復元
                if 'tire_width' in settings:
                    try:
                        width = int(settings['tire_width'])
                        if 23 <= width <= 50:
                            self.tire_width_value = width
                            self.tire_btn.title = f'{width}mm ▼'
                            self.calculator.set_tire_width(width)
                    except:
                        pass
                
                # 表示モードを復元
                if 'display_mode' in settings:
                    self.mode_segment.selected_index = settings['display_mode']
                    self.gear_scroll.hidden = settings['display_mode'] != 1
                
                # 選択された歯数を復元
                if 'selected_gears' in settings:
                    self.selected_gears = set(settings['selected_gears'])
                    # ボタンの表示を更新
                    for gear in self.selected_gears:
                        if gear in self.gear_buttons:
                            btn = self.gear_buttons[gear]
                            btn.background_color = COLORS['gear_btn_selected']
                            btn.tint_color = 'white'
                
                # 選択数を更新
                self.update_gear_count()
        except Exception as e:
            print(f'設定の読み込みに失敗: {e}')
    
    def get_number_keyboard_type(self):
        """利用可能な数字キーボードタイプを取得"""
        # Pythonistaで利用可能なキーボードタイプを順番に試す
        keyboard_types = [
            'KEYBOARD_NUMBER_PAD',
            'KEYBOARD_DECIMAL_PAD', 
            'KEYBOARD_NUMBERS_AND_PUNCTUATION',
            'KEYBOARD_DEFAULT'
        ]
        
        for kb_type in keyboard_types:
            if hasattr(ui, kb_type):
                return getattr(ui, kb_type)
        
        return ui.KEYBOARD_DEFAULT
    
    def setup_ui(self):
        """Pythonista UI をセットアップ"""
        self.view = MainView(self)
        self.view.name = '🚴 GearSpeed'
        self.view.background_color = COLORS['bg_primary']
        
        # メインビューをフルスクリーンに設定
        main_view = ui.View()
        main_view.background_color = COLORS['bg_primary']
        main_view.flex = 'WH'  # 幅・高さ両方向に伸縮
        
        # 入力コンテナ（横画面対応・上部に移動）
        input_container = ui.View()
        input_container.background_color = COLORS['bg_card']
        input_container.border_width = 0.5
        input_container.border_color = COLORS['border_light']
        input_container.corner_radius = 16
        input_container.frame = (10, 20, 300, 90)  # タイヤ幅をホイールと同じ行に配置
        input_container.flex = 'W'
        main_view.add_subview(input_container)
        self.input_container = input_container
        
        # フロントギア選択（プルダウン式）
        front_label = ui.Label()
        front_label.text = _('front_gear_label')
        front_label.font = ('<system-bold>', 13)
        front_label.text_color = COLORS['text_primary']
        front_label.frame = (12, 8, 80, 24)
        input_container.add_subview(front_label)
        
        # フロントギア選択ボタン（タップでリスト表示）
        self.front_btn = ui.Button()
        self.front_btn.title = '50T ▼'
        self.front_btn.font = ('<system>', 13)
        self.front_btn.background_color = COLORS['bg_elevated']
        self.front_btn.tint_color = COLORS['accent_blue']
        self.front_btn.border_width = 0.5
        self.front_btn.border_color = COLORS['border_light']
        self.front_btn.corner_radius = 8
        self.front_btn.frame = (95, 6, 60, 28)
        self.front_btn.action = self.select_front_gear
        input_container.add_subview(self.front_btn)
        self.front_gear_value = 50  # 選択された値を保持
        
        # ホイールサイズ選択
        wheel_label = ui.Label()
        wheel_label.text = _('wheel_label')
        wheel_label.font = ('<system-bold>', 12)
        wheel_label.text_color = COLORS['text_primary']
        wheel_label.frame = (12, 38, 55, 24)
        input_container.add_subview(wheel_label)
        
        self.wheel_segment = ui.SegmentedControl()
        self.wheel_segment.segments = ['700c', '650c']
        self.wheel_segment.selected_index = 0  # デフォルトは700c
        self.wheel_segment.frame = (65, 36, 80, 28)
        self.wheel_segment.action = self.wheel_size_changed
        input_container.add_subview(self.wheel_segment)
        
        # タイヤ幅選択（ホイールサイズの右側に配置）
        self.tire_label = ui.Label()
        self.tire_label.text = _('tire_width_label')
        self.tire_label.font = ('<system-bold>', 12)
        self.tire_label.text_color = COLORS['text_primary']
        self.tire_label.frame = (150, 38, 55, 24)
        input_container.add_subview(self.tire_label)
        
        # タイヤ幅選択ボタン
        self.tire_btn = ui.Button()
        self.tire_btn.title = '28mm ▼'
        self.tire_btn.font = ('<system>', 11)
        self.tire_btn.background_color = COLORS['bg_elevated']
        self.tire_btn.tint_color = COLORS['accent_blue']
        self.tire_btn.border_width = 0.5
        self.tire_btn.border_color = COLORS['border_light']
        self.tire_btn.corner_radius = 8
        self.tire_btn.frame = (205, 36, 70, 28)
        self.tire_btn.action = self.select_tire_width
        input_container.add_subview(self.tire_btn)
        
        # 速度表生成ボタン
        table_btn = ui.Button()
        table_btn.title = '▶️ ' + _('generate_btn')
        table_btn.font = ('<system-bold>', 11)
        table_btn.background_color = COLORS['btn_primary']
        table_btn.tint_color = 'white'
        table_btn.corner_radius = 10
        table_btn.frame = (165, 6, 90, 28)
        table_btn.action = self.generate_table
        input_container.add_subview(table_btn)
        
        # クリアボタン（速度表生成ボタンの右側に横並び配置）
        clear_btn = ui.Button()
        clear_btn.title = _('clear_btn')
        clear_btn.font = ('<system>', 11)
        clear_btn.background_color = COLORS['btn_danger']
        clear_btn.tint_color = 'white'
        clear_btn.corner_radius = 10
        clear_btn.frame = (260, 6, 50, 28)
        clear_btn.action = self.clear_results
        input_container.add_subview(clear_btn)
        
        # 共有ボタン（印刷・メール・AirDropなど）
        share_btn = ui.Button()
        share_btn.title = _('share_btn')
        share_btn.font = ('<system>', 14)
        share_btn.background_color = COLORS['btn_primary']
        share_btn.tint_color = 'white'
        share_btn.corner_radius = 14
        share_btn.frame = (315, 6, 28, 28)
        share_btn.action = self.share_table
        input_container.add_subview(share_btn)
        
        # ヘルプ/凡例ボタン（タップでメニュー表示）
        info_btn = ui.Button()
        info_btn.title = 'ℹ️'
        info_btn.font = ('<system>', 14)
        info_btn.background_color = COLORS['accent_purple']
        info_btn.tint_color = 'white'
        info_btn.corner_radius = 14
        info_btn.frame = (348, 6, 28, 28)
        info_btn.action = self.show_info_menu
        input_container.add_subview(info_btn)
        
        # 表示モード選択（全表示/カスタム）
        self.mode_label = ui.Label()
        self.mode_label.text = _('mode_label')
        self.mode_label.font = ('<system-bold>', 12)
        self.mode_label.text_color = COLORS['text_primary']
        self.mode_label.frame = (12, 68, 45, 24)
        input_container.add_subview(self.mode_label)
        
        self.mode_segment = ui.SegmentedControl()
        self.mode_segment.segments = [_('mode_all'), _('mode_custom')]
        self.mode_segment.selected_index = 0  # デフォルトは全表示
        self.mode_segment.frame = (55, 66, 110, 28)
        self.mode_segment.action = self.mode_changed
        input_container.add_subview(self.mode_segment)
        
        # ギア選択数表示ラベル（カスタムモード時のみ意味がある）
        self.gear_count_label = ui.Label()
        self.gear_count_label.text = _('selected_count', 0)
        self.gear_count_label.font = ('<system>', 11)
        self.gear_count_label.text_color = COLORS['text_tertiary']
        self.gear_count_label.frame = (168, 68, 60, 24)
        input_container.add_subview(self.gear_count_label)
        
        # ペーストボタン（クリップボードからギア構成を読み込む）
        self.paste_btn = ui.Button()
        self.paste_btn.title = _('paste_btn')
        self.paste_btn.font = ('<system>', 10)
        self.paste_btn.background_color = COLORS['accent_purple']
        self.paste_btn.tint_color = 'white'
        self.paste_btn.corner_radius = 8
        self.paste_btn.frame = (230, 66, 55, 28)
        self.paste_btn.action = self.paste_gear_config
        input_container.add_subview(self.paste_btn)
        
        # プリセット保存ボタン
        self.save_preset_btn = ui.Button()
        self.save_preset_btn.title = _('save_btn')
        self.save_preset_btn.font = ('<system>', 10)
        self.save_preset_btn.background_color = COLORS['btn_success']
        self.save_preset_btn.tint_color = 'white'
        self.save_preset_btn.corner_radius = 8
        self.save_preset_btn.frame = (288, 66, 50, 28)
        self.save_preset_btn.action = self.save_preset
        input_container.add_subview(self.save_preset_btn)
        
        # プリセット読込ボタン
        self.load_preset_btn = ui.Button()
        self.load_preset_btn.title = _('load_btn')
        self.load_preset_btn.font = ('<system>', 10)
        self.load_preset_btn.background_color = COLORS['btn_warning']
        self.load_preset_btn.tint_color = 'white'
        self.load_preset_btn.corner_radius = 8
        self.load_preset_btn.frame = (341, 66, 50, 28)
        self.load_preset_btn.action = self.load_preset
        input_container.add_subview(self.load_preset_btn)
        
        # プリセット削除ボタン
        self.delete_preset_btn = ui.Button()
        self.delete_preset_btn.title = _('delete_btn')
        self.delete_preset_btn.font = ('<system>', 10)
        self.delete_preset_btn.background_color = COLORS['btn_secondary']
        self.delete_preset_btn.tint_color = 'white'
        self.delete_preset_btn.corner_radius = 8
        self.delete_preset_btn.frame = (394, 66, 50, 28)
        self.delete_preset_btn.action = self.delete_preset
        input_container.add_subview(self.delete_preset_btn)
        
        # 歯数選択ボタンコンテナ（スクロール可能、初期は非表示）
        gear_scroll = ui.ScrollView()
        gear_scroll.background_color = COLORS['gear_scroll_bg']
        gear_scroll.border_width = 0.5
        gear_scroll.border_color = COLORS['border_light']
        gear_scroll.corner_radius = 12
        gear_scroll.frame = (10, 98, 280, 95)  # 初期値
        gear_scroll.hidden = True
        gear_scroll.shows_horizontal_scroll_indicator = False
        gear_scroll.shows_vertical_scroll_indicator = True
        input_container.add_subview(gear_scroll)
        self.gear_scroll = gear_scroll
        
        # ボタン用のコンテンツビュー
        self.gear_selector_container = ui.View()
        self.gear_selector_container.background_color = COLORS['gear_scroll_bg']
        gear_scroll.add_subview(self.gear_selector_container)
        
        # 歯数選択ボタンを作成
        self.create_gear_buttons()
        
        # カスタム表示エリア（操作メニューの直下に配置）
        self.table_container = ui.View()
        self.table_container.frame = (10, 120, 300, 200)  # 初期値は小さめに（layout_subviewsで調整）
        self.table_container.flex = 'WH'  # 幅・高さ両方向に伸縮
        self.table_container.border_width = 0.5
        self.table_container.border_color = COLORS['border_light']
        self.table_container.corner_radius = 16
        self.table_container.background_color = COLORS['bg_card']
        main_view.add_subview(self.table_container)
        
        # カスタム表を初期化（まだ表示しない）
        self.custom_table = CustomSpeedTable(self.table_container)
        
        # 初期メッセージ表示
        self.show_welcome_message()
        
        self.view.add_subview(main_view)
    
    def create_gear_buttons(self):
        """歯数選択ボタンを作成"""
        # 9から51までのすべての歯数
        all_gears = list(range(9, 52))  # 9-51
        
        # ボタンのサイズと配置
        self.btn_width = 35
        self.btn_height = 25
        self.btn_margin = 3
        self.x_offset = 3
        self.y_offset = 3
        
        for gear in all_gears:
            btn = ui.Button()
            btn.name = str(gear)
            btn.title = str(gear)
            btn.font = ('<system-bold>', 12)
            btn.background_color = COLORS['gear_btn_normal']
            btn.tint_color = COLORS['gear_btn_text']
            btn.border_width = 0
            btn.border_color = COLORS['border_light']
            btn.corner_radius = 8
            btn.action = self.toggle_gear_selection
            
            self.gear_selector_container.add_subview(btn)
            self.gear_buttons[gear] = btn
        
        # 初回のレイアウトを実行
        self.update_gear_buttons_layout()
    
    def update_gear_buttons_layout(self, scroll_width=None):
        """画面幅に応じてギアボタンのレイアウトを更新"""
        # スクロールビューの幅を取得（明示的に渡された場合はそれを使用）
        if scroll_width is None:
            scroll_width = self.gear_scroll.width
        scroll_width = max(scroll_width, 280)
        
        # 利用可能な幅から列数を計算
        # 最後の列の後にはマージンが不要なので、+btn_marginで調整
        available_width = scroll_width - self.x_offset * 2
        cols_per_row = max(1, int((available_width + self.btn_margin) / (self.btn_width + self.btn_margin)))
        
        # 9から51までのすべての歯数
        all_gears = list(range(9, 52))  # 9-51
        
        # ボタンを再配置
        for i, gear in enumerate(all_gears):
            row = i // cols_per_row
            col = i % cols_per_row
            
            btn = self.gear_buttons[gear]
            btn.frame = (self.x_offset + col * (self.btn_width + self.btn_margin), 
                        self.y_offset + row * (self.btn_height + self.btn_margin), 
                        self.btn_width, self.btn_height)
        
        # コンテンツサイズを計算
        total_rows = (len(all_gears) + cols_per_row - 1) // cols_per_row
        content_height = self.y_offset * 2 + total_rows * (self.btn_height + self.btn_margin)
        
        # コンテナの幅はスクロールビューの幅と同じにする（タッチイベントのため）
        self.gear_selector_container.frame = (0, 0, scroll_width, content_height)
        self.gear_scroll.content_size = (scroll_width, content_height)
    
    def toggle_gear_selection(self, sender):
        """歯数の選択/解除をトグル"""
        gear = int(sender.name)
        
        if gear in self.selected_gears:
            # 選択解除
            self.selected_gears.remove(gear)
            sender.background_color = COLORS['gear_btn_normal']
            sender.tint_color = COLORS['gear_btn_text']
        else:
            # 選択
            self.selected_gears.add(gear)
            sender.background_color = COLORS['gear_btn_selected']
            sender.tint_color = 'white'
        
        # 選択数を更新
        self.update_gear_count()
        
        # 設定を保存
        self.save_settings()
    
    def update_gear_count(self):
        """選択されたギア数の表示を更新"""
        count = len(self.selected_gears)
        self.gear_count_label.text = _('selected_count', count)
        # 選択数に応じて色を変更
        if count == 0:
            self.gear_count_label.text_color = COLORS['accent_red']  # 赤
        elif count <= 5:
            self.gear_count_label.text_color = COLORS['accent_orange']  # オレンジ
        else:
            self.gear_count_label.text_color = COLORS['accent_green']  # 緑
    
    def parse_gear_text(self, text):
        """テキストからギア構成を解析"""
        gears = set()
        
        # テキストを正規化（全角→半角、余分な空白除去）
        text = text.replace('　', ' ').replace('T', '').replace('t', '')
        text = text.replace('、', ',').replace('/', ',').replace('-', ',')
        text = text.replace('\n', ' ').replace('\r', ' ')
        
        # 数字を抽出するパターン
        # パターン1: カンマやスペース区切りの数字 (例: "11, 13, 15, 17")
        # パターン2: ハイフン区切りの範囲表記 (例: "11-13-15-17")
        # パターン3: 連続した数字の列 (例: "11-32" はカセット範囲を示す場合がある)
        
        # まずカンマやスペースで分割
        parts = re.split(r'[,\s]+', text)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # 数字のみを抽出
            try:
                num = int(re.sub(r'[^0-9]', '', part))
                if 9 <= num <= 51:  # 有効な歯数範囲
                    gears.add(num)
            except ValueError:
                continue
        
        return gears
    
    def paste_gear_config(self, sender):
        """クリップボードからギア構成を読み込んで設定"""
        try:
            text = clipboard.get()
            if not text:
                console.hud_alert(_('err_clipboard_empty'), 'error', 2)
                return
            
            # テキストからギア構成を解析
            parsed_gears = self.parse_gear_text(text)
            
            if not parsed_gears:
                console.hud_alert(_('err_no_gears_found'), 'error', 2)
                return
            
            # 既存の選択をクリア
            for gear, btn in self.gear_buttons.items():
                if gear in self.selected_gears:
                    btn.background_color = COLORS['gear_btn_normal']
                    btn.tint_color = COLORS['gear_btn_text']
            self.selected_gears.clear()
            
            # 新しいギア構成を設定
            for gear in parsed_gears:
                if gear in self.gear_buttons:
                    self.selected_gears.add(gear)
                    btn = self.gear_buttons[gear]
                    btn.background_color = COLORS['gear_btn_selected']
                    btn.tint_color = 'white'
            
            # カスタムモードに切り替え
            self.mode_segment.selected_index = 1
            self.gear_scroll.hidden = False
            
            # 選択数を更新
            self.update_gear_count()
            
            # 設定を保存
            self.save_settings()
            
            # 結果を表示
            sorted_gears = sorted(parsed_gears)
            console.hud_alert(_('paste_result', len(parsed_gears), sorted_gears), 'success', 3)
            
        except Exception as e:
            console.hud_alert(_('err_error', str(e)), 'error', 2)
    
    def mode_changed(self, sender):
        """表示モードが変更された時の処理"""
        is_custom = sender.selected_index == 1  # カスタムモード
        
        # 歯数選択コンテナの表示/非表示を切り替え
        self.gear_scroll.hidden = not is_custom
        
        # レイアウトを再調整
        self.layout_subviews()
        
        # 設定を保存
        self.save_settings()
    
    def wheel_size_changed(self, sender):
        """ホイールサイズが変更された時の処理"""
        wheel_sizes = ['700c', '650c']
        selected_wheel = wheel_sizes[sender.selected_index]
        self.calculator.set_wheel_size(selected_wheel)
        
        # 設定を保存
        self.save_settings()
        
        # 既に表が表示されている場合は再計算
        if hasattr(self, 'welcome_label') and self.welcome_label is None:
            self.generate_table(None)
    
    def select_tire_width(self, sender):
        """タイヤ幅をリストから選択"""
        # 23-50mmの選択肢を作成
        items = [f'{w}mm' for w in range(23, 51)]
        
        # 現在選択されている値のインデックスを取得
        current_index = self.tire_width_value - 23  # 23mmが0番目
        
        # カスタムダイアログを表示（選択位置にスクロール）
        selected = self.show_list_dialog_with_position(
            title=_('tire_width_label'), 
            items=items, 
            initial_index=current_index
        )
        
        if selected:
            # 選択された値を取得（例: "28mm" → 28）
            value = int(selected.replace('mm', ''))
            self.tire_width_value = value
            self.tire_btn.title = f'{value}mm ▼'
            self.calculator.set_tire_width(value)
            
            # 設定を保存
            self.save_settings()
            
            # 既に表が表示されている場合は再計算
            if hasattr(self, 'welcome_label') and self.welcome_label is None:
                self.generate_table(None)
    
    def select_front_gear(self, sender):
        """フロントギアをリストから選択"""
        # 20-60Tの選択肢を作成
        items = [f'{t}T' for t in range(20, 61)]
        
        # 現在選択されている値のインデックスを取得
        current_index = self.front_gear_value - 20  # 20Tが0番目
        
        # カスタムダイアログを表示（選択位置にスクロール）
        selected = self.show_list_dialog_with_position(
            title=_('front_gear_label'), 
            items=items, 
            initial_index=current_index
        )
        
        if selected:
            # 選択された値を取得（例: "50T" → 50）
            value = int(selected.replace('T', ''))
            self.front_gear_value = value
            self.front_btn.title = f'{value}T ▼'
            
            # 設定を保存
            self.save_settings()
            
            # 既に表が表示されている場合は再計算
            if hasattr(self, 'welcome_label') and self.welcome_label is None:
                self.generate_table(None)
    
    def show_list_dialog_with_position(self, title, items, initial_index=0):
        """初期位置を指定できるリストダイアログ（ダークモード対応）"""
        import ui
        import time
        
        # 結果を格納する変数
        result = {'selected': None}
        
        # ダイアログビューを作成
        dialog_view = ui.View()
        dialog_view.name = title
        dialog_view.background_color = COLORS['bg_primary']
        dialog_view.corner_radius = 16
        
        # テーブルビューを作成
        table = ui.TableView()
        table.flex = 'WH'
        table.background_color = COLORS['bg_primary']
        table.separator_color = COLORS['border_light']
        table.corner_radius = 12
        
        # 行の高さ（デフォルト値）
        row_height = 48  # やや高くしてタップしやすく
        
        # データソースを作成
        class ListDataSource:
            def __init__(self, items, result_dict, dialog, colors):
                self.items = items
                self.result = result_dict
                self.dialog = dialog
                self.colors = colors
            
            def tableview_number_of_rows(self, tableview, section):
                return len(self.items)
            
            def tableview_cell_for_row(self, tableview, section, row):
                cell = ui.TableViewCell()
                cell.text_label.text = self.items[row]
                cell.text_label.font = ('<system>', 16)
                cell.text_label.text_color = self.colors['text_primary']
                cell.background_color = self.colors['bg_primary']
                # 選択時の背景色
                cell.selected_background_view = ui.View()
                cell.selected_background_view.background_color = self.colors['bg_elevated']
                cell.selected_background_view.corner_radius = 8
                return cell
            
            def tableview_did_select(self, tableview, section, row):
                self.result['selected'] = self.items[row]
                self.dialog.close()
        
        data_source = ListDataSource(items, result, dialog_view, COLORS)
        table.data_source = data_source
        table.delegate = data_source
        
        dialog_view.add_subview(table)
        
        # スクロール位置を設定する関数
        def scroll_to_initial():
            if 0 <= initial_index < len(items):
                # 選択項目が画面の中央付近に来るようにスクロール
                scroll_y = max(0, initial_index * row_height - row_height * 2)
                table.content_offset = (0, scroll_y)
        
        # ダイアログを表示
        dialog_view.present('sheet')
        
        # 表示後に少し遅延してスクロール
        ui.delay(scroll_to_initial, 0.1)
        
        # ダイアログが閉じるまで待機
        dialog_view.wait_modal()
        
        return result['selected']
    
    def show_themed_list_dialog(self, title, items):
        """テーマ対応のリストダイアログ"""
        return self.show_list_dialog_with_position(title, items, initial_index=0)
    
    def generate_table(self, sender):
        """速度表を生成"""
        # ウェルカムメッセージを削除
        self.clear_welcome_message()
        
        try:
            front_gear = self.front_gear_value
            if front_gear < 20 or front_gear > 60:
                self.show_error(_('err_front_range'))
                return
            
            # ホイールサイズを設定
            wheel_sizes = ['700c', '650c']
            selected_wheel = wheel_sizes[self.wheel_segment.selected_index]
            self.calculator.set_wheel_size(selected_wheel)
            
            # タイヤ幅を設定
            self.calculator.set_tire_width(self.tire_width_value)
            
            # 表示モードに応じて歯数を決定
            rear_gears = None  # デフォルトは全表示
            if self.mode_segment.selected_index == 1:  # カスタムモード
                # 選択された歯数を取得
                if self.selected_gears:
                    rear_gears = sorted(list(self.selected_gears))
                else:
                    self.show_error(_('err_custom_select'))
                    return
            
            table_data = self.calculator.create_speed_table(front_gear, rear_gears)
            
            # データを保存（共有用）
            self.current_table_data = table_data
            self.current_front_gear = front_gear
            self.current_wheel_size = selected_wheel
            self.current_tire_width = self.tire_width_value
            
            # カスタム表を更新
            self.custom_table.update_data(table_data)
            
            # 設定を保存
            self.save_settings()
            
        except ValueError:
            self.show_error(_('err_invalid_number'))
    
    def show_welcome_message(self):
        """ウェルカムメッセージを表示"""
        # table_container内の全てのsubviewを削除
        for subview in list(self.table_container.subviews):
            self.table_container.remove_subview(subview)
        
        welcome_label = ui.Label()
        welcome_label.text = _('welcome_message')
        welcome_label.font = ('<system>', 16)
        welcome_label.text_color = COLORS['text_tertiary']
        welcome_label.alignment = ui.ALIGN_CENTER
        welcome_label.number_of_lines = 0
        # コンテナサイズに基づいてフレームを設定
        container_w = max(self.table_container.width, 100)
        container_h = max(self.table_container.height, 100)
        welcome_label.frame = (10, 10, container_w - 20, container_h - 20)
        welcome_label.flex = 'WH'
        self.table_container.add_subview(welcome_label)
        self.welcome_label = welcome_label
    
    def help_pressed(self, sender):
        """ヘルプダイアログを表示"""
        help_text = _('help_text')
        console.alert(_('help_title'), help_text, 'OK', hide_cancel_button=True)
    
    def show_table_legend(self, sender):
        """表の凡例を表示"""
        legend_text = _('legend_text')
        console.alert(_('legend_title'), legend_text, 'OK', hide_cancel_button=True)
    
    def show_info_menu(self, sender):
        """ヘルプ/凡例/テーマメニューを表示"""
        items = [_('help_title'), _('legend_title'), _('theme_title')]
        selected = self.show_themed_list_dialog('ℹ️', items)
        if selected == _('help_title'):
            self.help_pressed(None)
        elif selected == _('legend_title'):
            self.show_table_legend(None)
        elif selected == _('theme_title'):
            self.show_theme_menu()
    
    def show_theme_menu(self):
        """テーマ選択メニューを表示"""
        current_theme = get_theme_setting()
        
        # 現在のテーマにチェックマークを付ける
        items = []
        themes = ['auto', 'light', 'dark']
        labels = [_('theme_auto'), _('theme_light'), _('theme_dark')]
        
        for theme, label in zip(themes, labels):
            if theme == current_theme:
                items.append(f'✓ {label}')
            else:
                items.append(f'   {label}')
        
        selected = self.show_themed_list_dialog(_('theme_title'), items)
        
        if selected:
            # 選択からテーマを特定
            index = items.index(selected)
            new_theme = themes[index]
            
            if new_theme != current_theme:
                # テーマ設定を保存
                self.save_theme_setting(new_theme)
                console.hud_alert(_('theme_changed'), 'success', 2)
    
    def save_theme_setting(self, theme):
        """テーマ設定を保存"""
        try:
            settings = {}
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            
            settings['theme'] = theme
            
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f'テーマ設定の保存に失敗: {e}')
    
    def share_table(self, sender):
        """速度表を共有シートで共有"""
        if not self.current_table_data:
            console.hud_alert(_('share_no_data'), 'error', 2)
            return
        
        # HTML生成
        html_content = self.generate_html_table()
        
        # HTMLファイルとして保存してから共有
        try:
            # Pythonistaのドキュメントディレクトリに保存
            import os
            
            # ファイル名を生成（フロントギアとタイムスタンプ）
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'GearSpeed_{self.current_front_gear}T_{timestamp}.html'
            
            # ドキュメントディレクトリのパスを取得
            doc_path = os.path.expanduser('~/Documents')
            file_path = os.path.join(doc_path, filename)
            
            # HTMLファイルを保存
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # console.open_in()でHTMLファイルとして共有シートを表示
            console.open_in(file_path)
            
        except Exception as e:
            # フォールバック: クリップボードにコピー
            try:
                clipboard.set(html_content)
                console.hud_alert(_('share_clipboard'), 'success', 2)
            except:
                console.hud_alert(f'Error: {e}', 'error', 2)
    
    def generate_html_table(self):
        """現在の速度表データからHTMLを生成"""
        # タイトル
        if IS_JAPANESE:
            title = f'GearSpeed 速度表 - フロント{self.current_front_gear}T / {self.current_wheel_size} / {self.current_tire_width}mm'
        else:
            title = f'GearSpeed Speed Table - Front {self.current_front_gear}T / {self.current_wheel_size} / {self.current_tire_width}mm'
        
        # CSS
        css = '''
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 10px; }
            h2 { color: #2c3e50; text-align: center; margin-bottom: 15px; }
            table { border-collapse: collapse; width: 100%; max-width: 500px; margin: 0 auto; }
            th, td { border: 1px solid #bdc3c7; padding: 6px 4px; text-align: center; font-size: 12px; }
            th { background-color: #34495e; color: white; }
            .gear-col { background-color: #e9ecef; font-weight: bold; }
            .num-col { background-color: #3498db; color: white; font-weight: bold; }
            .footer { text-align: center; color: #7f8c8d; font-size: 10px; margin-top: 10px; }
        </style>
        '''
        
        # テーブルヘッダー
        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    {css}
</head>
<body>
    <h2>🚴 {title}</h2>
    <table>
        <tr>
            <th>#</th>
            <th>T</th>
            <th>Ratio</th>
            <th>ΔR</th>
            <th>70</th>
            <th>80</th>
            <th>90</th>
            <th>100</th>
            <th>110</th>
        </tr>
'''
        
        # データ行を追加
        for i, row in enumerate(self.current_table_data):
            ratio_diff = row.get('ratio_diff', '')
            ratio_diff_str = f"{ratio_diff:.2f}" if ratio_diff else '-'
            
            # 速度に応じた色を取得
            speed_colors = {
                '70': self.get_speed_html_color(row['70rpm']),
                '80': self.get_speed_html_color(row['80rpm']),
                '90': self.get_speed_html_color(row['90rpm']),
                '100': self.get_speed_html_color(row['100rpm']),
                '110': self.get_speed_html_color(row['110rpm']),
            }
            
            html += f'''        <tr>
            <td class="num-col">{i+1}</td>
            <td class="gear-col">{row['rear']}</td>
            <td>{row['gear_ratio']:.2f}</td>
            <td>{ratio_diff_str}</td>
            <td style="background-color:{speed_colors['70']}">{row['70rpm']:.1f}</td>
            <td style="background-color:{speed_colors['80']}">{row['80rpm']:.1f}</td>
            <td style="background-color:{speed_colors['90']}">{row['90rpm']:.1f}</td>
            <td style="background-color:{speed_colors['100']}">{row['100rpm']:.1f}</td>
            <td style="background-color:{speed_colors['110']}">{row['110rpm']:.1f}</td>
        </tr>
'''
        
        # フッター
        if IS_JAPANESE:
            footer = '速度 km/h @ ケイデンス rpm'
        else:
            footer = 'Speed km/h @ Cadence rpm'
        
        html += f'''    </table>
    <p class="footer">{footer}</p>
</body>
</html>'''
        
        return html
    
    def get_speed_html_color(self, speed):
        """速度に応じたHTML用色コードを返す"""
        speed = max(0, min(speed, 60))
        ratio = speed / 60.0
        
        if ratio <= 0.25:  # 0-15km/h: 青系
            r = int(52 + (100 - 52) * (ratio / 0.25))
            g = int(152 + (180 - 152) * (ratio / 0.25))  
            b = int(219 + (255 - 219) * (ratio / 0.25))
        elif ratio <= 0.5:  # 15-30km/h: 青 → 緑
            local_ratio = (ratio - 0.25) / 0.25
            r = int(100 + (76 - 100) * local_ratio)
            g = int(180 + (205 - 180) * local_ratio)
            b = int(255 + (92 - 255) * local_ratio)
        elif ratio <= 0.75:  # 30-45km/h: 緑 → 黄
            local_ratio = (ratio - 0.5) / 0.25
            r = int(76 + (255 - 76) * local_ratio)
            g = int(205 + (235 - 205) * local_ratio)
            b = int(92 + (59 - 92) * local_ratio)
        else:  # 45-60km/h: 黄 → 赤
            local_ratio = (ratio - 0.75) / 0.25
            r = int(255)
            g = int(235 + (99 - 235) * local_ratio)
            b = int(59 + (71 - 59) * local_ratio)
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def clear_welcome_message(self):
        """ウェルカムメッセージを削除し、表をセットアップ"""
        if hasattr(self, 'welcome_label') and self.welcome_label and self.welcome_label.superview:
            self.welcome_label.superview.remove_subview(self.welcome_label)
            self.welcome_label = None
        
        # カスタム表をセットアップ
        self.custom_table.setup_table()
    
    def get_named_presets(self):
        """保存されたプリセット一覧を取得"""
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    return settings.get('named_presets', {})
        except:
            pass
        return {}
    
    def save_named_preset(self, name, gears):
        """名前付きプリセットを保存"""
        try:
            settings = {}
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            
            if 'named_presets' not in settings:
                settings['named_presets'] = {}
            
            settings['named_presets'][name] = sorted(list(gears))
            
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f'プリセット保存エラー: {e}')
            return False
    
    def delete_named_preset(self, name):
        """名前付きプリセットを削除"""
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                if 'named_presets' in settings and name in settings['named_presets']:
                    del settings['named_presets'][name]
                    
                    with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                        json.dump(settings, f, ensure_ascii=False, indent=2)
                    return True
        except Exception as e:
            print(f'プリセット削除エラー: {e}')
        return False
    
    def save_preset(self, sender):
        """現在のギア設定を名前付きで保存"""
        if not self.selected_gears:
            console.hud_alert(_('err_select_gears_to_save'), 'error', 2)
            return
        
        try:
            # 初期値としてギア構成を生成（短縮形式: 11-34）
            sorted_gears = sorted(self.selected_gears)
            min_gear = sorted_gears[0]
            max_gear = sorted_gears[-1]
            default_name = f'{min_gear}-{max_gear}'
            
            name = console.input_alert(
                _('preset_save_title'),
                _('preset_save_prompt', len(self.selected_gears)),
                default_name,
                'OK'
            )
            
            if name and name.strip():
                name = name.strip()
                if self.save_named_preset(name, self.selected_gears):
                    console.hud_alert(_('preset_saved', name, sorted_gears), 'success', 2)
                else:
                    console.hud_alert(_('err_save_failed'), 'error', 2)
            else:
                console.hud_alert(_('err_enter_name'), 'error', 2)
        except KeyboardInterrupt:
            pass  # キャンセル
    
    def load_preset(self, sender):
        """保存したプリセットを読み込み"""
        presets = self.get_named_presets()
        
        if not presets:
            console.hud_alert(_('err_no_presets'), 'error', 2)
            return
        
        # プリセット一覧を作成
        preset_names = list(presets.keys())
        if IS_JAPANESE:
            items = [f'{name} ({len(presets[name])}枚)' for name in preset_names]
        else:
            items = [f'{name} ({len(presets[name])}T)' for name in preset_names]
        
        # リスト選択ダイアログを表示（カスタム）
        selected = self.show_themed_list_dialog(_('preset_load_title'), items)
        
        if selected:
            # 選択されたアイテムからプリセット名を取得
            index = items.index(selected)
            name = preset_names[index]
            gears = presets[name]
            
            # 既存の選択をクリア
            for gear, btn in self.gear_buttons.items():
                if gear in self.selected_gears:
                    btn.background_color = COLORS['gear_btn_normal']
                    btn.tint_color = COLORS['gear_btn_text']
            self.selected_gears.clear()
            
            # プリセットのギアを設定
            for gear in gears:
                if gear in self.gear_buttons:
                    self.selected_gears.add(gear)
                    btn = self.gear_buttons[gear]
                    btn.background_color = COLORS['gear_btn_selected']
                    btn.tint_color = 'white'
            
            # カスタムモードに切り替え
            self.mode_segment.selected_index = 1
            self.gear_scroll.hidden = False
            self.layout_subviews()
            
            # 選択数を更新
            self.update_gear_count()
            
            # 設定を保存
            self.save_settings()
            
            console.hud_alert(_('preset_loaded', name), 'success', 2)
    
    def delete_preset(self, sender):
        """保存したプリセットを削除"""
        presets = self.get_named_presets()
        
        if not presets:
            console.hud_alert(_('err_no_presets_to_delete'), 'error', 2)
            return
        
        # プリセット一覧を作成
        preset_names = list(presets.keys())
        if IS_JAPANESE:
            items = [f'{name} ({len(presets[name])}枚)' for name in preset_names]
        else:
            items = [f'{name} ({len(presets[name])}T)' for name in preset_names]
        
        # リスト選択ダイアログを表示（カスタム）
        selected = self.show_themed_list_dialog(_('preset_delete_title'), items)
        
        if selected:
            # 選択されたアイテムからプリセット名を取得
            index = items.index(selected)
            name = preset_names[index]
            
            # 確認ダイアログ
            try:
                console.alert(
                    _('preset_delete_confirm_title'),
                    _('preset_delete_confirm', name),
                    'OK'
                )
                if self.delete_named_preset(name):
                    console.hud_alert(_('preset_deleted', name), 'success', 2)
                else:
                    console.hud_alert(_('err_delete_failed'), 'error', 2)
            except KeyboardInterrupt:
                pass  # キャンセル
    
    def textfield_should_return(self, textfield):
        """Returnキーでキーボードを非表示"""
        textfield.end_editing()
        return True
    
    def hide_keyboard(self, sender):
        """キーボードを非表示にする"""
        self.front_field.end_editing()
    
    def clear_results(self, sender):
        """結果表示をクリアして初期画面に戻す"""
        # ウェルカムメッセージを表示
        self.show_welcome_message()
        
        # 選択された歯数をリセット
        self.selected_gears.clear()
        for gear, btn in self.gear_buttons.items():
            btn.background_color = COLORS['gear_btn_normal']
            btn.tint_color = COLORS['gear_btn_text']
        
        # 選択数を更新
        self.update_gear_count()
    
    def show_error(self, message):
        """エラーメッセージを表示"""
        console.hud_alert(_('err_error', message), 'error', 2)
    
    def layout_subviews(self):
        """画面回転時のレイアウト調整"""
        # ビューサイズを取得
        w, h = self.view.width, self.view.height
        
        # 横画面判定（幅 > 高さ）
        is_landscape = w > h
        
        # カスタムモードかどうかで入力コンテナの高さを変更
        is_custom_mode = self.mode_segment.selected_index == 1
        if is_custom_mode:
            input_height = 200  # カスタムモード時は歯数選択エリアを含む
        else:
            input_height = 100   # 全表示モード時
        
        # input_containerの幅を計算
        container_width = w - 20
        
        if is_landscape:
            # 横画面レイアウト
            self.input_container.frame = (10, 10, container_width, input_height)
            table_top = input_height + 20
            self.table_container.frame = (10, table_top, container_width, h - table_top - 10)
        else:
            # 縦画面レイアウト
            self.input_container.frame = (10, 20, container_width, input_height)
            table_top = input_height + 30
            self.table_container.frame = (10, table_top, container_width, h - table_top - 10)
        
        margin = 12
        
        # 2行目: ホイール + タイヤ幅（画面幅に応じて配置）
        row2_y = 36
        if hasattr(self, 'tire_label'):
            self.tire_label.frame = (150, row2_y + 2, 55, 24)
        if hasattr(self, 'tire_btn'):
            self.tire_btn.frame = (205, row2_y, 70, 28)
        
        # 3行目: モード + 選択数 + ペースト + 保存/読込/削除
        row3_y = 66
        # 左側: モード切替
        if hasattr(self, 'mode_label'):
            self.mode_label.frame = (margin, row3_y + 2, 45, 24)
        if hasattr(self, 'mode_segment'):
            self.mode_segment.frame = (margin + 43, row3_y, 110, 28)
        if hasattr(self, 'gear_count_label'):
            self.gear_count_label.frame = (margin + 156, row3_y + 2, 60, 24)
        
        # 右側: ペースト + 保存/読込/削除（画面幅に応じて右寄せ）
        btn_w = 50
        btn_gap = 3
        total_btns_width = btn_w * 4 + btn_gap * 3  # 4つのボタン
        right_x = container_width - margin - total_btns_width
        
        if hasattr(self, 'paste_btn'):
            self.paste_btn.frame = (right_x, row3_y, btn_w, 28)
        if hasattr(self, 'save_preset_btn'):
            self.save_preset_btn.frame = (right_x + btn_w + btn_gap, row3_y, btn_w, 28)
        if hasattr(self, 'load_preset_btn'):
            self.load_preset_btn.frame = (right_x + (btn_w + btn_gap) * 2, row3_y, btn_w, 28)
        if hasattr(self, 'delete_preset_btn'):
            self.delete_preset_btn.frame = (right_x + (btn_w + btn_gap) * 3, row3_y, btn_w, 28)

        # ギアスクロールの幅を更新（input_containerの幅を基準に、左右10pxマージン）
        gear_scroll_width = container_width - 24
        self.gear_scroll.frame = (12, 100, gear_scroll_width, 95)
        
        # ギアボタンのレイアウトを更新（明示的に幅を渡す）
        self.update_gear_buttons_layout(gear_scroll_width)
        
        # カスタム表のレイアウトを更新
        if self.custom_table:
            self.custom_table.update_layout(self.table_container.width, self.table_container.height)
    
    def run(self):
        """アプリを実行"""
        self.view.present('sheet')
        # 表示後に明示的にレイアウトを調整
        self.layout_subviews()
        # ウェルカムメッセージを再表示（正しいサイズで）
        if self.welcome_label:
            self.show_welcome_message()

# Pythonistaで実行
if __name__ == '__main__':
    app = BikeSpeedApp()
    app.run()
