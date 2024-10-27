using System;
using System.Collections;
using System.Collections.Generic;

using UnityEngine;
using UnityEngine.UI;


public class FlasherControl : MonoBehaviour
{
   

    Image image;

    public TMPro.TMP_InputField input;

    public float waitTime = 1f;


    void Start()
        {
            image = GetComponent<Image>();
        }


    IEnumerator Blink()
        {
            while (true)
            {
                switch (image.color.a.ToString())
                {
                    case "0":
                        image.color = new Color(image.color.r, image.color.g, image.color.b, 1);
                        //Play sound
                        yield return new WaitForSeconds(waitTime);
                        break;
                    case "1":
                        image.color = new Color(image.color.r, image.color.g, image.color.b, 0);
                        //Play sound
                        yield return new WaitForSeconds(waitTime);
                        break;
                }
            }
        }

    void StartBlinking()
        {
            StopAllCoroutines();
            StartCoroutine("Blink");
        }
        
    void StopBlinking()
        {
            StopAllCoroutines();
        }

    public void OnStartClick()
    {
        StartBlinking();
    }
    public void OnStopClick()
    {
        StopBlinking();
    }
    public void OnInputUpdate()
    {
        int inputVal  = Int32.Parse(input.text);
        waitTime = 1f / inputVal;
    }

}
