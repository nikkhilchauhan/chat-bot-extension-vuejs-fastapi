<template>
  <div class="main-popup-container">
    <div class="header">
      <div class="row">
        <div class="col-12 d-flex justify-content-center align-items-center">
          <span class="badge rounded-pill text-bg-success">{{
            greetingMsg
          }}</span>
        </div>

        <div class="row" v-if="isLoading">
          <div
            class="col-12 d-flex justify-content-center align-items-center mt-3"
          >
            <div class="spinner-border" role="status"></div>
          </div>
          <p class="small text-info text-center">
            Fetching data, please wait...
          </p>
        </div>

        <div
          class="col-12 d-flex justify-content-center align-items-center mt-3"
        >
          <div
            v-if="!isInitialLoaded"
            class="spinner-border"
            role="status"
          ></div>
        </div>
        <p v-if="!isInitialLoaded" class="small text-info text-center">
          Checking server status...
        </p>
        <p v-if="isServerError" class="text-danger text-center">
          Something went wrong while connecting to the server!
        </p>
      </div>
    </div>

    <div v-if="isInitialLoaded" id="chat-messages">
      <div v-for="item in chats.init_chat" :key="item.id">
        <div class="{ message: true, right: item.sender == 1 }">
          <div
            v-if="item.msg_type == 'text'"
            :class="{
              bubble: true,
              textDanger: item.type == 'error',
              sendColor: item.sender == 1,
              senderBubble: item.sender == 1,
              receiverBubble: item.sender == 0,
            }"
          >
            {{ item.msg }}
          </div>
          <div
            v-if="item.msg_type == 'search'"
            :class="{
              bubble: true,
              textDanger: item.type == 'error',
              sendColor: item.sender == 1,
              senderBubble: item.sender == 1,
              receiverBubble: item.sender == 0,
            }"
          >
            <div
              class="search-msg"
              v-for="(msgs, index) in item.msg"
              :key="index"
            >
              <span>
                {{
                  this.readMoreIndex === index ? msgs : msgs.substring(0, 50)
                }}
                <span class="readmorebtn" @click="setReadType(index)">
                  {{ this.isReadMore ? 'Read less' : 'Read more...' }}</span
                >
              </span>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="isInitialLoaded && !selectedAction && !isServerError"
        class="action-btn-container"
      >
        <div @click="downloadTapped" class="action-btn">
          Download my current active tab data (.txt)
        </div>
        <div @click="searchTapped" class="action-btn ms-3">
          Search something from the available data
        </div>
      </div>
    </div>

    <div v-if="selectedAction == 'search'" class="search-input">
      <div id="sendmessage">
        <input
          :value="searchInput"
          @input="(event) => (searchInput = event.target.value)"
          @keyup.enter="searchApiCall()"
          type="text"
          style="color: black"
          placeholder="Type something..."
        />
        <button @click="closeSearch()" id="close"></button>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  data() {
    return {
      isLoading: false,
      greetingMsg: 'Loading...',
      isReadMore: false,
      readMoreIndex: null,
      isServerError: false,
      isInitialLoaded: false, //boolean only
      isActionCompleted: false, //boolean only
      selectedAction: null, // download, search
      searchInput: '',
      chats: {
        init_chat: [],
      },
      icons: {
        active: 'images/icon-48x48.png',
        inactive: 'images/icon-48x48-off.png',
      },
    };
  },
  created() {
    const today = new Date();
    const curHr = today.getHours();
    if (curHr < 12) {
      this.greetingMsg = 'Good Morning!';
    } else if (curHr < 18) {
      this.greetingMsg = 'Good Afternoon!';
    } else {
      this.greetingMsg = 'Good Evening!';
    }
    this.checkServerStatus();
  },
  methods: {
    closeSearch() {
      this.selectedAction = null;
      this.chats.init_chat.push({
        msg: 'Please select an option',
        msg_type: 'text',
        type: 'success',
        sender: 0,
      });
    },
    saveTextAsFile(textToWrite, fileNameToSaveAs, fileType) {
      let textFileAsBlob = new Blob([textToWrite], { type: fileType });
      let downloadLink = document.createElement('a');
      downloadLink.download = fileNameToSaveAs;
      downloadLink.innerHTML = 'Download File';

      if (window.webkitURL != null) {
        downloadLink.href = window.webkitURL.createObjectURL(textFileAsBlob);
      } else {
        downloadLink.href = window.URL.createObjectURL(textFileAsBlob);
        downloadLink.style.display = 'none';
        document.body.appendChild(downloadLink);
      }
      downloadLink.click();
      this.closeSearch();
    },
    async downloadApiCall(url) {
      try {
        this.isLoading = true;
        const response = await fetch(
          `http://127.0.0.1:8000/download?url=${url}`
        );
        if (response.status == 200) {
          this.isLoading = false;
          const data = await response.json();
          this.saveTextAsFile(data['data'], 'tabData', '.txt');
        } else {
          this.isLoading = false;
          this.chats.init_chat.push({
            msg: 'Something went wrong!',
            msg_type: 'text',
            type: 'error',
            sender: 0,
          });
        }
      } catch (error) {
        this.isLoading = false;
        this.chats.init_chat.push({
          msg: 'Something went wrong!',
          msg_type: 'text',
          type: 'error',
          sender: 0,
        });
      }
    },
    async searchApiCall() {
      try {
        this.isLoading = true;
        const response = await fetch(
          `http://127.0.0.1:8000/search?term=${this.searchInput}`
        );
        if (response.status == 200) {
          this.isLoading = false;
          const data = await response.json();
          this.searchInput = '';
          if (data['data'].length > 0) {
            this.chats.init_chat.push({
              msg: data['data'],
              msg_type: 'search',
              type: 'success',
              sender: 0,
            });
          } else {
            this.chats.init_chat.push({
              msg: 'No match found for your search term!',
              msg_type: 'text',
              type: 'error',
              sender: 0,
            });
          }
        } else {
          this.isLoading = false;
          this.chats.init_chat.push({
            msg: 'Something went wrong!',
            msg_type: 'text',
            type: 'error',
            sender: 0,
          });
        }
      } catch (error) {
        this.isLoading = false;
        this.chats.init_chat.push({
          msg: 'Something went wrong!',
          msg_type: 'text',
          type: 'error',
          sender: 0,
        });
      }
    },
    downloadTapped() {
      const that = this;
      this.chats.init_chat.push({
        msg: 'Download my current active tab data (.txt)',
        msg_type: 'text',
        type: 'success',
        sender: 1,
      });
      this.selectedAction = 'download';
      chrome.tabs.query({ currentWindow: true, active: true }, function (tabs) {
        if (!!tabs.length > 0) {
          that.downloadApiCall(tabs[0]['url']);
        }
      });
    },
    searchTapped() {
      this.chats.init_chat.push({
        msg: 'Search something from the available data',
        msg_type: 'text',
        type: 'success',
        sender: 1,
      });
      this.selectedAction = 'search';
    },
    async checkServerStatus() {
      try {
        const response = await fetch('http://127.0.0.1:8000');
        if (response.status == 200) {
          this.chats.init_chat.push({
            msg: 'Hi, please select an option',
            msg_type: 'text',
            type: 'success',
            sender: 0,
          });
          this.isServerError = false;
          this.isInitialLoaded = true;
        }
      } catch (error) {
        this.isServerError = true;
      }
    },
    setReadType(index) {
      if (index === this.readMoreIndex) {
        this.isReadMore = false;
        this.readMoreIndex = null;
      } else {
        this.isReadMore = true;
        this.readMoreIndex = index;
      }
    },
  },
};
</script>
