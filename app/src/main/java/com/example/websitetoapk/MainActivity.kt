package com.example.websitetoapk

import android.os.Bundle
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webView)
        setupWebView()

        // The URL for the WebView will be injected here by the GitHub Action
        // KEEP THIS AS A UNIQUE PLACEHOLDER STRING
        val targetUrl = "WEBVIEW_TARGET_URL_PLACEHOLDER"
        webView.loadUrl(targetUrl)
    }

    private fun setupWebView() {
        webView.webViewClient = WebViewClient()
        val webSettings: WebSettings = webView.settings
        webSettings.javaScriptEnabled = true // Enable JavaScript
        webSettings.domStorageEnabled = true // Enable DOM storage
        webSettings.loadWithOverviewMode = true
        webSettings.useWideViewPort = true
        webSettings.builtInZoomControls = true // Enable zoom controls
        webSettings.displayZoomControls = false // Hide the zoom controls
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}