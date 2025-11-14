<template>
  <div class="search-result-item">
    <h1 class="search-title">{{ item.title }}</h1>
    <p class="search-snippet">{{ item.snippet }}</p>
    <!-- <a :href="item.link" target="_blank">了解更多</a> -->
  </div>
</template>

<script>
export default {
  name: 'SearchResult',
  props: {
    item: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style scoped>
.search-result-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
  background-color: #fff;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.search-title {
  color: blue;
  font-size: 1.5em;
  margin-bottom: 10px;

}

.search-snippet {
  margin-bottom: 10px;
}

a {
  color: #007bff;
  text-decoration: none;
  font-size: 0.9em;
}

a:hover {
  text-decoration: underline;
}
</style>