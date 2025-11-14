<template>
    <div>
      <div id="paypal-button-container"></div>
    </div>
  </template>
  
  <script>
  export default {
    mounted() {
      // PayPal SDK 加载
      const script = document.createElement("script");
      script.src = "https://www.paypal.com/sdk/js?client-id=AU6Y6MglaHTUKTrnMNiLzmHlyMYJsm6pXhSwUsiL2414zZO6SbDvEtzkU5KtQWBb05lYdQ_dZMxgk2O_&currency=USD";
      script.onload = this.renderPayPalButton;
      document.body.appendChild(script);
    },
    
    methods: {
      renderPayPalButton() {
        window.paypal.Buttons({
          createOrder: async () => {
            const response = await fetch("https://finaisearch.com/api/create-order", {
              method: "POST",
            });
            const data = await response.json();
            return data.id; // 返回订单 ID
          },
          onApprove: async (data) => {
            const response = await fetch(`https://finaisearch.com/api/capture-order/${data.orderID}`, {
              method: "POST",
            });
            const result = await response.json();
            console.log("支付成功: ", result);
            alert("支付成功！");
          },
          onError: (err) => {
            console.error("支付失败: ", err);
            alert("支付失败，请重试！");
          },
        }).render("#paypal-button-container");
      },
    },
  };
  </script>
  
  <style scoped>
  /* 可选样式 */
  </style>
  