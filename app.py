import streamlit as st
import dropbox

# --- 1. Dropbox設定 ---
TOKEN = st.secrets["DROPBOX_TOKEN"]
dbx = dropbox.Dropbox(TOKEN)

st.set_page_config(page_title="Text File Explorer", layout="centered")
st.title("📂 Text File Explorer")

# --- 2. 状態の管理 ---
if "current_path" not in st.session_state:
    st.session_state.current_path = "" 
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

# リストを取得
entries = list_folder(st.session_state.current_path)

# 【改良点】フォルダと「.txtファイル」だけを抽出
folders = [e for e in entries if isinstance(e, dropbox.files.FolderMetadata)]
# ファイル名が .txt で終わるものだけをリストアップします
text_files = [e for e in entries if isinstance(e, dropbox.files.FileMetadata) and e.name.lower().endswith('.txt')]

# --- 4. 画面表示 ---

# フォルダを表示
for folder in folders:
    if st.button(f"📁 {folder.name}", key=folder.path_lower, use_container_width=True):
        st.session_state.current_path = folder.path_display
        st.rerun()

# テキストファイルのみを表示
for file in text_files:
    if st.button(f"📄 {file.name}", key=file.path_lower, use_container_width=True):
        st.session_state.editing_file = file.path_display
        # ファイル内容を読み込む
        _, res = dbx.files_download(file.path_display)
        st.session_state.content = res.content.decode("utf-8")
        st.rerun()

st.divider()

# --- 5. 編集画面 ---
if st.session_state.editing_file:
    st.subheader(f"編集: {st.session_state.editing_file.split('/')[-1]}")
    
    new_content = st.text_area("内容を編集", value=st.session_state.content, height=350)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 上書き保存", use_container_width=True):
            dbx.files_upload(new_content.encode("utf-8"), st.session_state.editing_file, mode=dropbox.files.WriteMode.overwrite)
            st.success("保存完了！")
    with col2:
        if st.button("❌ 閉じる", use_container_width=True):
            st.session_state.editing_file = None
            st.rerun()
