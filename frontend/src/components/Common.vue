<template>
    
</template>

<script>
  const BASEHOST = 'http://127.0.0.1:5000/webapp/';
  export default {
        name: "Common",
        BASEHOST,
        error: function (title, nodesc) {
            this.$Notice.error({
              title: title,
              desc: nodesc ? nodesc : ''
            });
        }
    }
</script>

<style scoped>

</style>
