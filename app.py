import streamlit as st
import dropbox

# --- 1. Dropbox設定 ---
TOKEN = st.secrets["DROPBOX_TOKEN"]
dbx = dropbox.Dropbox(TOKEN)

st.set_page_config(page_title="Dropbox Explorer", layout="centered")
st.title("📂 Dropbox Explorer")

# --- 2. 状態の管理 ---
if "current_path" not in st.session_state:
    st.session_state.current_path = "" # ルートディレクトリ
if "editing_file" not in st.session_state:
    st.session_state.editing_file = None
if "content" not in st.session_state:
    st.session_state.content = ""

# --- 3. フォルダ探索機能 ---
def list_folder(path):
    try:
        res = dbx.files_list_folder(path)
        return res.entries
    except Exception as e:
        st.error(f"エラー: {e}")
        return []

# 上の階層へ戻るボタン
if st.session_state.current_path != "":
    if st.button("⬅️ 一つ上のフォルダへ"):
        parts = st.session_state.current_path.split("/")
        st.session_state.current_path = "/".join(parts[:-1])
        st.rerun()

st.write(f"現在の場所: `{st.session_state.current_path or '/'}`")

# ファイルとフォルダの一覧を表示
entries = list_folder(st.session_state.current_path)
folders = [e for e in entries if isinstance(e, dropbox.files.FolderMetadata)]
files = [e for e in entries if isinstance(e, dropbox.files.FileMetadata)]

# フォルダの選択
for folder in folders:
    if st.button(f"📁 {folder.name}", key=folder.path_lower):
        st.session_state.current_path = folder.path_display
        st.rerun()

# ファイルの選択
for file in files:
    if st.button(f"📄 {file.name}", key=file.path_lower):
        st.session_state.editing_file = file.path_display
        # ファイル内容を読み込む
        _, res = dbx.files_download(file.path_display)
        st.session_state.content = res.content.decode("utf-8")
        st.rerun()

st.divider()

# --- 4. 編集画面 (ファイルが選択されている場合のみ表示) ---
if st.session_state.editing_file:
    st.subheader(f"編集中のファイル: {st.session_state.editing_file}")
    
    # 以前作成した編集・履歴・保存機能
    new_content = st.text_area("内容を編集", value=st.session_state.content, height=300)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 このファイルに上書き保存", use_container_width=True):
            dbx.files_upload(new_content.encode("utf-8"), st.session_state.editing_file, mode=dropbox.files.WriteMode.overwrite)
            st.success("保存しました！")
    with col2:
        if st.button("❌ 編集を閉じる", use_container_width=True):
            st.session_state.editing_file = None
            st.rerun()
