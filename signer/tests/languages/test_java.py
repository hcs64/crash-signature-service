from signer.languages.java import JavaSignatureTool


class TestSignatureToolBase(object):
    def test_generate(self):
        inst = JavaSignatureTool()

        frames = [
            (
                'java.lang.IllegalArgumentException: Given view not a child '
                'of android.widget.AbsoluteLayout@4054b560'
            ),
            'at android.view.ViewGroup.updateViewLayout(ViewGroup.java:1968)',
            (
                'at org.mozilla.gecko.GeckoApp.repositionPluginViews'
                '(GeckoApp.java:1492)'
            ),
            (
                'at org.mozilla.gecko.GeckoApp.repositionPluginViews'
                '(GeckoApp.java:1475)'
            ),
            (
                'at org.mozilla.gecko.gfx.LayerController$2.run'
                '(LayerController.java:269)'
            ),
            'at android.os.Handler.handleCallback(Handler.java:587)',
            'at android.os.Handler.dispatchMessage(Handler.java:92)',
            'at android.os.Looper.loop(Looper.java:150)',
            'at org.mozilla.gecko.GeckoApp$32.run(GeckoApp.java:1670)',
            'at android.os.Handler.handleCallback(Handler.java:587)',
            'at android.os.Handler.dispatchMessage(Handler.java:92)',
            'at android.os.Looper.loop(Looper.java:150)',
            'at android.app.ActivityThread.main(ActivityThread.java:4293)',
            'at java.lang.reflect.Method.invokeNative(Native Method)',
            'at java.lang.reflect.Method.invoke(Method.java:507)',
            (
                'at com.android.internal.os.ZygoteInit$MethodAndArgsCaller.run'
                '(ZygoteInit.java:849)'
            ),
            'at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:607)',
            'at dalvik.system.NativeStart.main(Native Method)',
        ]
        signature, _ = inst.generate(frames)

        assert signature == (
            'java.lang.IllegalArgumentException: '
            'Given view not a child of android.widget.AbsoluteLayout@<addr>: '
            'at android.view.ViewGroup.updateViewLayout(ViewGroup.java)'
        )
